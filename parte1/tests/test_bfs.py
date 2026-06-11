from pathlib import Path
import sys

import pytest


PART1_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PART1_DIR))

from src.graphs.algorithms import bfs
from src.graphs.io import build_airport_graph


@pytest.fixture(scope="module")
def graph():
    """Carrega uma única vez o grafo real utilizado pela Parte 1."""
    return build_airport_graph(
        str(PART1_DIR / "data" / "aeroportos_data.csv"),
        str(PART1_DIR / "data" / "adjacencias_aeroportos.csv")
    )


def test_bfs_iniciado_em_rec_visita_rec(graph):
    order = bfs(graph, "REC")

    assert order[0] == "REC"


def test_bfs_visita_todos_os_aeroportos_do_grafo(graph):
    order = bfs(graph, "REC")

    assert set(order) == set(graph.nodes())


def test_bfs_nao_repete_vertices(graph):
    order = bfs(graph, "REC")

    assert len(order) == len(set(order))
