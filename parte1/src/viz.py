from pathlib import Path
import json

import pandas as pd
import matplotlib.pyplot as plt

from src.graphs.io import build_airport_graph
from src.graphs.algorithms import bfs_layers, dijkstra


DATA_DIR = Path("data")
OUT_DIR = Path("out")

AIRPORTS_PATH = DATA_DIR / "aeroportos_data.csv"
ADJACENCIES_PATH = DATA_DIR / "adjacencias_aeroportos.csv"
PASSENGERS_PATH = DATA_DIR / "passageiros.csv"

GRAUS_PATH = OUT_DIR / "graus.csv"
REGIOES_PATH = OUT_DIR / "regioes.json"
EGO_PATH = OUT_DIR / "ego_aeroportos.csv"


def ensure_out_dir() -> None:
    """
    Garante que a pasta out/ exista.
    """
    OUT_DIR.mkdir(exist_ok=True)


def check_file_exists(path: Path) -> None:
    """
    Verifica se um arquivo existe antes de tentar carregá-lo.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {path}. "
            "Execute primeiro: python -m src.solve"
        )


def save_figure(path_out: Path) -> None:
    """
    Salva a figura atual em alta resolução e fecha o gráfico.
    """
    path_out.parent.mkdir(exist_ok=True)
    plt.tight_layout()
    plt.savefig(path_out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Arquivo gerado: {path_out}")


def read_csv_data(
    path: Path,
    required_columns: set[str],
    description: str
) -> pd.DataFrame:
    """Carrega um CSV e valida as colunas obrigatórias."""
    check_file_exists(path)
    df = pd.read_csv(path)
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"O arquivo {description} não possui as colunas: {missing}")

    return df


def read_passenger_data(path: Path) -> pd.DataFrame:
    """Carrega e normaliza os dados de passageiros por aeroporto."""
    df = read_csv_data(
        path,
        {"iata", "passageiros_milhoes"},
        "de passageiros"
    )
    df["iata"] = df["iata"].astype(str).str.strip().str.upper()
    df["passageiros_milhoes"] = (
        df["passageiros_milhoes"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )
    return df


def merge_degrees_and_passengers(
    degrees_path: Path,
    passengers_path: Path
) -> pd.DataFrame:
    """Combina passageiros e graus, mantendo aeroportos presentes no grafo."""
    graus_df = read_csv_data(
        degrees_path,
        {"aeroporto", "grau"},
        "de graus"
    )
    passageiros_df = read_passenger_data(passengers_path)

    graus_df["aeroporto"] = (
        graus_df["aeroporto"].astype(str).str.strip().str.upper()
    )
    graus_df["grau"] = pd.to_numeric(graus_df["grau"], errors="raise")

    return passageiros_df.merge(
        graus_df[["aeroporto", "grau"]],
        left_on="iata",
        right_on="aeroporto",
        how="inner"
    )


def style_axes(
    ax,
    title: str,
    xlabel: str,
    ylabel: str,
    grid_axis: str = "y"
) -> None:
    """Aplica o padrão visual compartilhado pelos gráficos do dashboard."""
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(axis=grid_axis, linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)


def add_bar_labels(ax, bars, formatter) -> None:
    """Adiciona os valores acima das barras sem encostar no limite do eixo."""
    heights = [float(bar.get_height()) for bar in bars]
    offset = max(heights, default=0) * 0.015 or 0.05

    for bar, height in zip(bars, heights):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + offset,
            formatter(height),
            ha="center",
            va="bottom",
            fontsize=9
        )

    ax.margins(y=0.12)


def plot_top_airports(path_in: Path, path_out: Path, top_n: int = 10) -> None:
    """
    Gera um gráfico de barras ordenado com os aeroportos de maior grau.
    """
    df = read_csv_data(path_in, {"aeroporto", "grau"}, "de graus")
    df["grau"] = pd.to_numeric(df["grau"], errors="raise")
    df_sorted = df.sort_values(
        by=["grau", "aeroporto"],
        ascending=[False, True]
    ).head(top_n)

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(
        df_sorted["aeroporto"],
        df_sorted["grau"],
        color="#3b82f6",
        edgecolor="black",
        label="Grau dos aeroportos"
    )

    style_axes(
        ax,
        f"Ranking de Graus dos Aeroportos — Top {top_n}",
        "Aeroportos — código IATA",
        "Grau — número de conexões diretas"
    )
    ax.legend()
    add_bar_labels(ax, bars, lambda value: str(int(value)))

    save_figure(path_out)


def plot_passenger_ranking(
    path_in: Path,
    path_out: Path,
    top_n: int = 10
) -> None:
    """Gera o ranking dos aeroportos com maior volume de passageiros."""
    df = read_passenger_data(path_in)
    df_sorted = df.sort_values(
        by=["passageiros_milhoes", "iata"],
        ascending=[False, True]
    ).head(top_n)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(
        df_sorted["iata"],
        df_sorted["passageiros_milhoes"],
        color="#f97316",
        edgecolor="black",
        label="Passageiros"
    )

    style_axes(
        ax,
        f"Ranking de Passageiros por Aeroporto — Top {top_n}",
        "Aeroportos — código IATA",
        "Passageiros anuais — milhões"
    )
    ax.legend()
    add_bar_labels(ax, bars, lambda value: f"{value:.1f}")
    save_figure(path_out)


def plot_passengers_by_region(
    passengers_path: Path,
    regions_path: Path,
    airports_path: Path,
    degrees_path: Path,
    path_out: Path
) -> None:
    """Soma os passageiros por região considerando aeroportos presentes no grafo."""
    check_file_exists(regions_path)

    with open(regions_path, "r", encoding="utf-8") as file:
        regions_data = json.load(file)

    regions_df = pd.DataFrame(regions_data)
    if "regiao" not in regions_df.columns:
        raise ValueError("O arquivo regioes.json não possui a chave 'regiao'.")

    airports_df = read_csv_data(
        airports_path,
        {"iata", "regiao"},
        "de aeroportos"
    )
    airports_df["iata"] = airports_df["iata"].astype(str).str.strip().str.upper()

    comparison_df = merge_degrees_and_passengers(degrees_path, passengers_path)
    comparison_df = comparison_df.merge(
        airports_df[["iata", "regiao"]],
        on="iata",
        how="left"
    )

    passengers_by_region = (
        comparison_df
        .groupby("regiao")["passageiros_milhoes"]
        .sum()
        .reindex(regions_df["regiao"].tolist(), fill_value=0)
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(
        passengers_by_region.index,
        passengers_by_region.values,
        color="#22c55e",
        edgecolor="black",
        label="Passageiros por região"
    )

    style_axes(
        ax,
        "Passageiros por Região",
        "Região",
        "Passageiros anuais — milhões"
    )
    ax.legend()
    add_bar_labels(ax, bars, lambda value: f"{value:.1f}")
    save_figure(path_out)


def plot_degree_vs_passengers(
    degrees_path: Path,
    passengers_path: Path,
    path_out: Path
) -> None:
    """Gera o scatter plot da relação entre grau e volume de passageiros."""
    df = merge_degrees_and_passengers(degrees_path, passengers_path)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(
        df["grau"],
        df["passageiros_milhoes"],
        s=80,
        color="#22c55e",
        edgecolor="black",
        alpha=0.85,
        label="Aeroportos"
    )

    for _, group in df.groupby("grau"):
        ordered_group = group.sort_values(by="passageiros_milhoes")
        center = (len(ordered_group) - 1) / 2

        for position, row in enumerate(ordered_group.itertuples(index=False)):
            vertical_offset = (position - center) * 12
            ax.annotate(
                row.iata,
                (row.grau, row.passageiros_milhoes),
                xytext=(6, vertical_offset),
                textcoords="offset points",
                fontsize=8,
                va="center"
            )

    style_axes(
        ax,
        "Relação entre Grau e Passageiros",
        "Grau — número de conexões diretas",
        "Passageiros anuais — milhões",
        grid_axis="both"
    )
    ax.legend()
    save_figure(path_out)


def plot_top_ego_density(path_in: Path, path_out: Path, top_n: int = 10) -> None:
    """
    Gera um gráfico de barras ordenado com as maiores densidades ego.
    """
    df = read_csv_data(
        path_in,
        {"aeroporto", "grau", "densidade_ego"},
        "de ego-network"
    )
    df["grau"] = pd.to_numeric(df["grau"], errors="raise")
    df["densidade_ego"] = pd.to_numeric(
        df["densidade_ego"],
        errors="raise"
    )
    df_sorted = df.sort_values(
        by=["densidade_ego", "grau", "aeroporto"],
        ascending=[False, False, True]
    ).head(top_n)

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(
        df_sorted["aeroporto"],
        df_sorted["densidade_ego"],
        color="#a855f7",
        edgecolor="black",
        label="Densidade ego"
    )

    style_axes(
        ax,
        f"Top {top_n} Aeroportos por Densidade Ego",
        "Aeroportos — código IATA",
        "Densidade ego"
    )
    ax.set_ylim(0, 1.12)
    ax.legend()
    add_bar_labels(ax, bars, lambda value: f"{value:.2f}")

    save_figure(path_out)


def plot_passengers_per_connection(
    degrees_path: Path,
    passengers_path: Path,
    path_out: Path,
    top_n: int = 10
) -> None:
    """Gera o ranking de passageiros por conexão direta do aeroporto."""
    df = merge_degrees_and_passengers(degrees_path, passengers_path)
    df = df[df["grau"] > 0].copy()
    df["passageiros_por_conexao"] = (
        df["passageiros_milhoes"] / df["grau"]
    )
    df_sorted = df.sort_values(
        by=["passageiros_por_conexao", "iata"],
        ascending=[False, True]
    ).head(top_n)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(
        df_sorted["iata"],
        df_sorted["passageiros_por_conexao"],
        color="#06b6d4",
        edgecolor="black",
        label="Passageiros por conexão direta"
    )

    style_axes(
        ax,
        f"Passageiros por Conexão Direta — Top {top_n}",
        "Aeroportos — código IATA",
        "Milhões de passageiros por conexão"
    )
    ax.legend()
    add_bar_labels(ax, bars, lambda value: f"{value:.2f}")

    save_figure(path_out)


def plot_bfs_layers(path_out: Path, start: str = "REC") -> None:
    """
    Visualização explanatória:
    Mostra as camadas BFS a partir de um aeroporto inicial.

    A camada 0 é o aeroporto inicial.
    A camada 1 são seus vizinhos diretos.
    A camada 2 são aeroportos alcançados com duas arestas, e assim por diante.
    """

    graph = build_airport_graph(
        str(AIRPORTS_PATH),
        str(ADJACENCIES_PATH)
    )

    if not graph.has_node(start):
        raise ValueError(f"Aeroporto inicial não encontrado no grafo: {start}")

    layers = bfs_layers(graph, start)

    grouped_layers = {}

    for airport, layer in layers.items():
        grouped_layers.setdefault(layer, []).append(airport)

    positions = {}

    for layer, airports in grouped_layers.items():
        airports = sorted(airports)

        for index, airport in enumerate(airports):
            y = index - (len(airports) - 1) / 2
            positions[airport] = (layer, y)

    fig, ax = plt.subplots(figsize=(12, 7))

    # Desenha as arestas existentes entre os nós posicionados
    first_edge = True

    for origem, destino, _ in graph.edges():
        if origem in positions and destino in positions:
            x1, y1 = positions[origem]
            x2, y2 = positions[destino]

            ax.plot(
                [x1, x2],
                [y1, y2],
                linewidth=0.8,
                alpha=0.35,
                color="gray",
                label="Arestas do grafo" if first_edge else None
            )

            first_edge = False

    # Desenha os nós
    xs = []
    ys = []

    for airport, (x, y) in positions.items():
        xs.append(x)
        ys.append(y)

    ax.scatter(
        xs,
        ys,
        s=700,
        color="lightblue",
        edgecolor="black",
        label="Aeroportos",
        zorder=3
    )

    for airport, (x, y) in positions.items():
        ax.text(
            x,
            y,
            airport,
            ha="center",
            va="center",
            fontsize=9,
            fontweight="bold",
            zorder=4
        )

    ax.set_title(
        f"Camadas BFS a partir de {start}",
        fontsize=14,
        fontweight="bold",
        pad=15
    )
    ax.set_xlabel("Camada BFS — distância em número de arestas", fontsize=12)
    ax.set_ylabel("Aeroportos distribuídos por camada", fontsize=12)
    ax.grid(alpha=0.25)
    ax.legend()

    save_figure(path_out)


def get_path_edges(path: list[str]) -> set[tuple[str, str]]:
    """
    Converte um caminho em um conjunto de arestas não direcionadas.

    Exemplo:
    ["REC", "GRU", "POA"]
    vira:
    {("GRU", "REC"), ("GRU", "POA")}
    """

    edges = set()

    for index in range(len(path) - 1):
        origem = path[index]
        destino = path[index + 1]
        edges.add(tuple(sorted([origem, destino])))

    return edges


def plot_route_tree(path_out: Path) -> None:
    """
    Visualização obrigatória:
    Gera uma árvore/subgrafo de percurso para as rotas obrigatórias:

    - Recife -> Porto Alegre: REC -> POA
    - Manaus -> São Paulo: MAO -> GRU
    """

    graph = build_airport_graph(
        str(AIRPORTS_PATH),
        str(ADJACENCIES_PATH)
    )

    route_rec_poa = dijkstra(graph, "REC", "POA")
    route_mao_gru = dijkstra(graph, "MAO", "GRU")

    path_1 = route_rec_poa["caminho"]
    path_2 = route_mao_gru["caminho"]

    edges_1 = get_path_edges(path_1)
    edges_2 = get_path_edges(path_2)

    fig, ax = plt.subplots(figsize=(12, 6))

    positions = {}

    # Rota REC -> POA na linha superior
    for index, airport in enumerate(path_1):
        positions[(airport, "rota1")] = (index, 1)

    # Rota MAO -> GRU na linha inferior
    for index, airport in enumerate(path_2):
        positions[(airport, "rota2")] = (index, -1)

    # Desenha rota 1
    for index in range(len(path_1) - 1):
        origem = path_1[index]
        destino = path_1[index + 1]

        x1, y1 = positions[(origem, "rota1")]
        x2, y2 = positions[(destino, "rota1")]

        ax.plot(
            [x1, x2],
            [y1, y2],
            linewidth=3,
            color="darkorange",
            label="REC → POA" if index == 0 else None
        )

    # Desenha rota 2
    for index in range(len(path_2) - 1):
        origem = path_2[index]
        destino = path_2[index + 1]

        x1, y1 = positions[(origem, "rota2")]
        x2, y2 = positions[(destino, "rota2")]

        ax.plot(
            [x1, x2],
            [y1, y2],
            linewidth=3,
            color="royalblue",
            label="MAO → GRU" if index == 0 else None
        )

    # Desenha os nós da rota 1
    for airport in path_1:
        x, y = positions[(airport, "rota1")]

        ax.scatter(
            x,
            y,
            s=900,
            color="moccasin",
            edgecolor="black",
            zorder=3
        )

        ax.text(
            x,
            y,
            airport,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            zorder=4
        )

    # Desenha os nós da rota 2
    for airport in path_2:
        x, y = positions[(airport, "rota2")]

        ax.scatter(
            x,
            y,
            s=900,
            color="lightsteelblue",
            edgecolor="black",
            zorder=3
        )

        ax.text(
            x,
            y,
            airport,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            zorder=4
        )

    ax.set_title(
        "Árvore de Percurso — Rotas Obrigatórias",
        fontsize=14,
        fontweight="bold",
        pad=15
    )

    ax.set_xlabel("Sequência do caminho mínimo", fontsize=12)
    ax.set_ylabel("Rotas obrigatórias", fontsize=12)

    ax.set_yticks([-1, 1])
    ax.set_yticklabels([
        f"MAO → GRU | custo {route_mao_gru['custo']:.2f} km",
        f"REC → POA | custo {route_rec_poa['custo']:.2f} km"
    ])

    ax.grid(alpha=0.25)
    ax.legend()

    text = (
        f"Caminho REC → POA: {' → '.join(path_1)}\n"
        f"Caminho MAO → GRU: {' → '.join(path_2)}"
    )

    plt.figtext(
        0.5,
        -0.05,
        text,
        ha="center",
        fontsize=9
    )

    save_figure(path_out)


def generate_visualization_notes(path_out: Path) -> None:
    """
    Gera um arquivo Markdown com as visualizações atuais do dashboard.
    """

    content = """# Notas Analíticas das Visualizações

## 1. Ranking de Graus dos Aeroportos

**Arquivo:** `out/ranking_graus.png`

Compara os aeroportos com maior número de conexões diretas e evidencia os hubs
estruturais da rede.

## 2. Ranking de Passageiros por Aeroporto

**Arquivo:** `out/ranking_passageiros.png`

Apresenta os aeroportos com maior movimentação anual de passageiros, em milhões.

## 3. Passageiros por Região

**Arquivo:** `out/passageiros_por_regiao.png`

Soma o tráfego dos aeroportos presentes no grafo e permite comparar a concentração
de passageiros entre as regiões listadas em `regioes.json`.

## 4. Relação Grau x Passageiros

**Arquivo:** `out/grau_x_passageiros.png`

Compara conectividade estrutural e movimentação operacional para verificar se
aeroportos com maior grau também tendem a receber mais passageiros.

## 5. Top Aeroportos por Densidade Ego

**Arquivo:** `out/top_ego_densidade.png`

Destaca aeroportos inseridos em vizinhanças locais mais interconectadas.

## 6. Passageiros por Conexão Direta

**Arquivo:** `out/passageiros_por_conexao.png`

Relaciona o volume de passageiros ao grau de cada aeroporto e evidencia operações
com tráfego elevado em relação ao número de conexões modeladas.
"""

    path_out.parent.mkdir(exist_ok=True)

    with open(path_out, "w", encoding="utf-8") as file:
        file.write(content)

    print(f"Arquivo gerado: {path_out}")


def main() -> None:
    """
    Gera as seis visualizações atuais do dashboard da aplicação.
    """

    ensure_out_dir()

    plot_top_airports(
        GRAUS_PATH,
        OUT_DIR / "ranking_graus.png",
        top_n=10
    )

    plot_passenger_ranking(
        PASSENGERS_PATH,
        OUT_DIR / "ranking_passageiros.png",
        top_n=10
    )

    plot_passengers_by_region(
        PASSENGERS_PATH,
        REGIOES_PATH,
        AIRPORTS_PATH,
        GRAUS_PATH,
        OUT_DIR / "passageiros_por_regiao.png"
    )

    plot_degree_vs_passengers(
        GRAUS_PATH,
        PASSENGERS_PATH,
        OUT_DIR / "grau_x_passageiros.png"
    )

    plot_top_ego_density(
        EGO_PATH,
        OUT_DIR / "top_ego_densidade.png",
        top_n=10
    )

    plot_passengers_per_connection(
        GRAUS_PATH,
        PASSENGERS_PATH,
        OUT_DIR / "passageiros_por_conexao.png",
        top_n=10
    )

    generate_visualization_notes(
        OUT_DIR / "notas_visualizacoes.md"
    )

    print("\nVisualizações geradas com sucesso.")


if __name__ == "__main__":
    main()
