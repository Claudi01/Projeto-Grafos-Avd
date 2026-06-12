import pytest
from src.graphs.graph import Graph
from src.graphs.algorithms import bfs_layers

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

def test_bfs_niveis(grafo_pequeno):
    niveis = bfs_layers(grafo_pequeno, "A")
    
    assert niveis["A"] == 0
    assert niveis["B"] == 1 
    assert niveis["C"] == 1 
    assert niveis["D"] == 2