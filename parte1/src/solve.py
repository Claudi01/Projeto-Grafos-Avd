import json
from pathlib import Path

import pandas as pd

from src.graphs.io import build_airport_graph
from src.graphs.algorithms import dijkstra


DATA_DIR = Path("data")
OUT_DIR = Path("out")

AIRPORTS_PATH = DATA_DIR / "aeroportos_data.csv"
ADJACENCIES_PATH = DATA_DIR / "adjacencias_aeroportos.csv"
ROUTES_PATH = DATA_DIR / "rotas.csv"


def ensure_out_dir():
    """
    Garante que a pasta out/ exista.
    """

    OUT_DIR.mkdir(exist_ok=True)


def calculate_density(order: int, size: int, directed: bool = False) -> float:
    """
    Calcula a densidade de um grafo.

    Para grafo não direcionado:
    densidade = 2E / V(V - 1)

    Para grafo direcionado:
    densidade = E / V(V - 1)
    """

    if order < 2:
        return 0.0

    if directed:
        return size / (order * (order - 1))

    return (2 * size) / (order * (order - 1))


def generate_global_metrics(graph):
    """
    Gera o arquivo out/global.json com:
    - ordem;
    - tamanho;
    - densidade.
    """

    data = {
        "ordem": graph.order(),
        "tamanho": graph.size(),
        "densidade": round(graph.density(), 4)
    }

    output_path = OUT_DIR / "global.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print(f"Arquivo gerado: {output_path}")


def generate_region_metrics(graph):
    """
    Gera o arquivo out/regioes.json.

    Para cada região, calcula:
    - ordem: quantidade de aeroportos da região;
    - tamanho: quantidade de arestas internas da região;
    - densidade: densidade do subgrafo induzido pela região.
    """

    regions = {}

    for node in graph.nodes():
        attrs = graph.get_node_attrs(node)
        region = attrs["regiao"]

        if region not in regions:
            regions[region] = []

        regions[region].append(node)

    result = []

    for region, nodes in regions.items():
        region_nodes = set(nodes)

        internal_edges = [
            (origem, destino)
            for origem, destino, _ in graph.edges()
            if origem in region_nodes and destino in region_nodes
        ]

        ordem = len(region_nodes)
        tamanho = len(internal_edges)
        densidade = calculate_density(ordem, tamanho, directed=False)

        result.append({
            "regiao": region,
            "ordem": ordem,
            "tamanho": tamanho,
            "densidade": round(densidade, 4)
        })

    result = sorted(result, key=lambda item: item["regiao"])

    output_path = OUT_DIR / "regioes.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=4)

    print(f"Arquivo gerado: {output_path}")


def generate_degrees(graph):
    """
    Gera o arquivo out/graus.csv.

    Colunas:
    - aeroporto;
    - grau.
    """

    rows = []

    for node in graph.nodes():
        rows.append({
            "aeroporto": node,
            "grau": graph.degree(node)
        })

    df = pd.DataFrame(rows)
    df = df.sort_values(by=["grau", "aeroporto"], ascending=[False, True])

    output_path = OUT_DIR / "graus.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"Arquivo gerado: {output_path}")


def generate_ego_metrics(graph):
    """
    Gera o arquivo out/ego_aeroportos.csv.

    Para cada aeroporto v, considera a ego-network:
    v + todos os seus vizinhos.

    Calcula:
    - aeroporto;
    - grau;
    - ordem_ego;
    - tamanho_ego;
    - densidade_ego.
    """

    rows = []

    all_edges = graph.edges()

    for node in graph.nodes():
        neighbors = set(graph.neighbors(node))
        ego_nodes = {node} | neighbors

        ego_edges = [
            (origem, destino)
            for origem, destino, _ in all_edges
            if origem in ego_nodes and destino in ego_nodes
        ]

        ordem_ego = len(ego_nodes)
        tamanho_ego = len(ego_edges)
        densidade_ego = calculate_density(ordem_ego, tamanho_ego, directed=False)

        rows.append({
            "aeroporto": node,
            "grau": graph.degree(node),
            "ordem_ego": ordem_ego,
            "tamanho_ego": tamanho_ego,
            "densidade_ego": round(densidade_ego, 4)
        })

    df = pd.DataFrame(rows)
    df = df.sort_values(by=["densidade_ego", "grau", "aeroporto"], ascending=[False, False, True])

    output_path = OUT_DIR / "ego_aeroportos.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"Arquivo gerado: {output_path}")


def load_routes():
    """
    Carrega o arquivo data/rotas.csv.

    Espera as colunas:
    origem,destino
    """

    if not ROUTES_PATH.exists():
        raise FileNotFoundError(
            "Arquivo data/rotas.csv não encontrado. "
            "Crie o arquivo antes de gerar as distâncias."
        )

    df = pd.read_csv(ROUTES_PATH)
    df.columns = [col.strip().lower() for col in df.columns]

    required_columns = {"origem", "destino"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes em rotas.csv: {missing}")

    df["origem"] = df["origem"].astype(str).str.strip().str.upper()
    df["destino"] = df["destino"].astype(str).str.strip().str.upper()

    return df


def generate_route_distances(graph):
    """
    Gera o arquivo out/distancias_rotas.csv.

    Para cada par origem-destino em data/rotas.csv,
    calcula o menor caminho usando Dijkstra.
    """

    df_routes = load_routes()

    rows = []

    for _, row in df_routes.iterrows():
        origem = row["origem"]
        destino = row["destino"]

        result = dijkstra(graph, origem, destino)

        caminho = " -> ".join(result["caminho"])

        rows.append({
            "origem": origem,
            "destino": destino,
            "custo": round(result["custo"], 2),
            "caminho": caminho
        })

    df = pd.DataFrame(rows)

    output_path = OUT_DIR / "distancias_rotas.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"Arquivo gerado: {output_path}")


def show_summary(graph):
    """
    Exibe um resumo no terminal.
    """

    print("\n=== RESUMO DO GRAFO ===")
    print(f"Ordem: {graph.order()}")
    print(f"Tamanho: {graph.size()}")
    print(f"Densidade: {round(graph.density(), 4)}")

    degrees = [(node, graph.degree(node)) for node in graph.nodes()]
    most_connected = max(degrees, key=lambda item: item[1])

    print(f"Aeroporto mais conectado: {most_connected[0]} | grau {most_connected[1]}")


def main():
    """
    Função principal para gerar os arquivos obrigatórios.
    """

    ensure_out_dir()

    graph = build_airport_graph(
        str(AIRPORTS_PATH),
        str(ADJACENCIES_PATH)
    )

    generate_global_metrics(graph)
    generate_region_metrics(graph)
    generate_degrees(graph)
    generate_ego_metrics(graph)
    generate_route_distances(graph)

    show_summary(graph)

    print("\nProcessamento concluído com sucesso.")


if __name__ == "__main__":
    main()