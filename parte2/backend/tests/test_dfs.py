import pytest
from src.graphs.graph import Graph
from src.graphs.algorithms import dfs

@pytest.fixture
def grafo_pequeno():
    g = Graph(directed=False)
    g.add_node("A")
    g.add_node("B")
    g.add_node("C")
    g.add_node("D")
    
    g.add_edge("A", "B", peso=1)
    g.add_edge("A", "C", peso=1)
    g.add_edge("C", "D", peso=1)
    return g

def test_dfs_visita_todos(grafo_pequeno):
    visitados = dfs(grafo_pequeno, "A")
    
    assert "A" in visitados
    assert "D" in visitados
    assert len(visitados) == 4