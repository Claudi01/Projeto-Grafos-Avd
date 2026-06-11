from pathlib import Path
import sys

import pytest


PART1_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PART1_DIR))

from src.graphs.algorithms import dijkstra
from src.graphs.io import build_airport_graph


@pytest.fixture(scope="module")
def graph():
    """Carrega uma única vez o grafo real utilizado pela Parte 1."""
    return build_airport_graph(
        str(PART1_DIR / "data" / "aeroportos_data.csv"),
        str(PART1_DIR / "data" / "adjacencias_aeroportos.csv")
    )


@pytest.mark.parametrize(
    ("origin", "destination"),
    [
        ("REC", "POA"),
        ("MAO", "GRU"),
    ]
)
def test_dijkstra_encontra_rota_valida(graph, origin, destination):
    result = dijkstra(graph, origin, destination)
    path = result["caminho"]

    assert path
    assert path[0] == origin
    assert path[-1] == destination
    assert result["custo"] > 0
    assert all(graph.has_node(airport) for airport in path)
