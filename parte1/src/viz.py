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


def plot_degree_histogram(path_in: Path, path_out: Path) -> None:
    """
    Visualização exploratória:
    Gera um histograma da distribuição de graus dos aeroportos.
    """

    check_file_exists(path_in)

    df = pd.read_csv(path_in)

    if "grau" not in df.columns:
        raise ValueError("O arquivo de graus não possui a coluna 'grau'.")

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.hist(
        df["grau"],
        bins=10,
        color="skyblue",
        edgecolor="black",
        label="Frequência dos graus"
    )

    ax.set_title(
        "Distribuição de Graus dos Aeroportos",
        fontsize=14,
        fontweight="bold",
        pad=15
    )
    ax.set_xlabel("Grau — número de conexões diretas", fontsize=12)
    ax.set_ylabel("Quantidade de aeroportos", fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.legend()

    save_figure(path_out)


def plot_top_airports(path_in: Path, path_out: Path, top_n: int = 10) -> None:
    """
    Visualização explanatória:
    Gera um gráfico de barras com o ranking dos aeroportos mais conectados.
    """

    check_file_exists(path_in)

    df = pd.read_csv(path_in)

    required_columns = {"aeroporto", "grau"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"O arquivo de graus não possui as colunas: {missing}")

    df_sorted = df.sort_values(by="grau", ascending=False).head(top_n)

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(
        df_sorted["aeroporto"],
        df_sorted["grau"],
        color="coral",
        edgecolor="black",
        label="Grau dos aeroportos"
    )

    ax.set_title(
        f"Top {top_n} Aeroportos Mais Conectados",
        fontsize=14,
        fontweight="bold",
        pad=15
    )
    ax.set_xlabel("Aeroportos — código IATA", fontsize=12)
    ax.set_ylabel("Grau — número de conexões diretas", fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.legend()

    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.2,
            str(int(height)),
            ha="center",
            va="bottom",
            fontsize=9
        )

    save_figure(path_out)


def plot_region_density(path_in: Path, path_out: Path) -> None:
    """
    Visualização exploratória/explanatória:
    Gera um gráfico de barras comparando a densidade interna das regiões.
    """

    check_file_exists(path_in)

    with open(path_in, "r", encoding="utf-8") as file:
        data = json.load(file)

    df = pd.DataFrame(data)

    required_columns = {"regiao", "densidade"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"O arquivo regioes.json não possui as chaves: {missing}")

    df = df.sort_values(by="densidade", ascending=False)

    fig, ax = plt.subplots(figsize=(9, 6))

    bars = ax.bar(
        df["regiao"],
        df["densidade"],
        color="mediumseagreen",
        edgecolor="black",
        label="Densidade regional"
    )

    ax.set_title(
        "Densidade dos Subgrafos por Região",
        fontsize=14,
        fontweight="bold",
        pad=15
    )
    ax.set_xlabel("Região", fontsize=12)
    ax.set_ylabel("Densidade interna do subgrafo", fontsize=12)
    ax.set_ylim(0, 1)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.legend()

    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.02,
            f"{height:.2f}",
            ha="center",
            va="bottom",
            fontsize=9
        )

    save_figure(path_out)


def plot_ego_density_histogram(path_in: Path, path_out: Path) -> None:
    """
    Visualização exploratória:
    Gera um histograma da distribuição da densidade das ego-networks.
    """

    check_file_exists(path_in)

    df = pd.read_csv(path_in)

    if "densidade_ego" not in df.columns:
        raise ValueError("O arquivo deve conter a coluna 'densidade_ego'.")

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.hist(
        df["densidade_ego"],
        bins=10,
        color="orchid",
        edgecolor="black",
        label="Frequência da densidade ego"
    )

    ax.set_title(
        "Distribuição da Densidade das Ego-Networks",
        fontsize=14,
        fontweight="bold",
        pad=15
    )
    ax.set_xlabel("Densidade ego", fontsize=12)
    ax.set_ylabel("Quantidade de aeroportos", fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.legend()

    save_figure(path_out)


def plot_top_ego_density(path_in: Path, path_out: Path, top_n: int = 10) -> None:
    """
    Visualização explanatória:
    Mostra os aeroportos com maior densidade ego.
    """

    check_file_exists(path_in)

    df = pd.read_csv(path_in)

    required_columns = {"aeroporto", "densidade_ego"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"O arquivo de ego-network não possui as colunas: {missing}")

    df_sorted = df.sort_values(
        by="densidade_ego",
        ascending=False
    ).head(top_n)

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(
        df_sorted["aeroporto"],
        df_sorted["densidade_ego"],
        color="slateblue",
        edgecolor="black",
        label="Densidade ego"
    )

    ax.set_title(
        f"Top {top_n} Aeroportos por Densidade Ego",
        fontsize=14,
        fontweight="bold",
        pad=15
    )
    ax.set_xlabel("Aeroportos — código IATA", fontsize=12)
    ax.set_ylabel("Densidade ego", fontsize=12)
    ax.set_ylim(0, 1)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.legend()

    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.02,
            f"{height:.2f}",
            ha="center",
            va="bottom",
            fontsize=9
        )

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
    Gera um arquivo Markdown com notas analíticas curtas
    para serem aproveitadas no PDF técnico.
    """

    content = """# Notas Analíticas das Visualizações

## 1. Histograma da Distribuição de Graus

**Arquivo:** `out/histograma_graus.png`

**Tipo:** visualização exploratória.

Esta visualização mostra como os graus dos aeroportos estão distribuídos no grafo. O grau representa a quantidade de conexões diretas de cada aeroporto. O histograma permite observar se a rede possui muitos aeroportos com baixa conectividade ou se há concentração em aeroportos com alto número de conexões. Esse tipo de gráfico foi escolhido porque é adequado para representar a distribuição de uma variável numérica.

## 2. Ranking dos Aeroportos Mais Conectados

**Arquivo:** `out/ranking_graus.png`

**Tipo:** visualização explanatória.

Esta visualização apresenta os aeroportos com maior grau no grafo. O gráfico de barras facilita a identificação dos principais hubs estruturais da rede. A mensagem principal é destacar quais aeroportos concentram mais conexões diretas e, portanto, exercem maior papel de integração no modelo construído.

## 3. Densidade dos Subgrafos por Região

**Arquivo:** `out/densidade_regioes.png`

**Tipo:** visualização exploratória e comparativa.

Esta visualização compara a densidade interna dos subgrafos regionais. A densidade indica o quanto os aeroportos de uma mesma região estão conectados entre si em relação ao máximo possível de conexões. O gráfico de barras foi escolhido porque permite comparar categorias regionais de forma direta e legível.

## 4. Histograma da Densidade das Ego-Networks

**Arquivo:** `out/histograma_ego_densidade.png`

**Tipo:** visualização exploratória.

Esta visualização mostra a distribuição das densidades ego dos aeroportos. A densidade ego mede o nível de conectividade local formado por um aeroporto e seus vizinhos diretos. O histograma permite analisar se a rede possui muitos aeroportos inseridos em vizinhanças locais densas ou se predominam ego-redes menos conectadas.

## 5. Top Aeroportos por Densidade Ego

**Arquivo:** `out/top_ego_densidade.png`

**Tipo:** visualização explanatória.

Esta visualização destaca os aeroportos com maior densidade ego. Diferentemente do grau, que mede apenas o número de conexões diretas, a densidade ego mostra se os vizinhos de um aeroporto também estão conectados entre si. Assim, essa visualização ajuda a identificar aeroportos localizados em subestruturas locais mais coesas.

## 6. Camadas BFS a partir de Recife

**Arquivo:** `out/camadas_bfs_rec.png`

**Tipo:** visualização explanatória.

Esta visualização mostra a distância estrutural dos aeroportos em relação a Recife, considerando o número de arestas necessárias para alcançar cada nó. A BFS percorre o grafo em camadas, tornando essa visualização adequada para representar níveis de alcance dentro da rede.

## 7. Árvore de Percurso das Rotas Obrigatórias

**Arquivo:** `out/arvore_percurso.png`

**Tipo:** visualização obrigatória de percurso.

Esta visualização apresenta os caminhos mínimos calculados pelo algoritmo de Dijkstra para as rotas Recife → Porto Alegre e Manaus → São Paulo. O objetivo é evidenciar a sequência de aeroportos percorrida e o custo total acumulado, considerando os pesos definidos no arquivo de adjacências.
"""

    path_out.parent.mkdir(exist_ok=True)

    with open(path_out, "w", encoding="utf-8") as file:
        file.write(content)

    print(f"Arquivo gerado: {path_out}")


def main() -> None:
    """
    Executa todas as visualizações do projeto.
    """

    ensure_out_dir()

    plot_degree_histogram(
        GRAUS_PATH,
        OUT_DIR / "histograma_graus.png"
    )

    plot_top_airports(
        GRAUS_PATH,
        OUT_DIR / "ranking_graus.png",
        top_n=10
    )

    plot_region_density(
        REGIOES_PATH,
        OUT_DIR / "densidade_regioes.png"
    )

    plot_ego_density_histogram(
        EGO_PATH,
        OUT_DIR / "histograma_ego_densidade.png"
    )

    plot_top_ego_density(
        EGO_PATH,
        OUT_DIR / "top_ego_densidade.png",
        top_n=10
    )

    plot_bfs_layers(
        OUT_DIR / "camadas_bfs_rec.png",
        start="REC"
    )

    plot_route_tree(
        OUT_DIR / "arvore_percurso.png"
    )

    generate_visualization_notes(
        OUT_DIR / "notas_visualizacoes.md"
    )

    print("\nVisualizações geradas com sucesso.")


if __name__ == "__main__":
    main()