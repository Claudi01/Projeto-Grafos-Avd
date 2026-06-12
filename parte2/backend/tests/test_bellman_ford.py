import pytest
from src.graphs.graph import Graph
from src.graphs.algorithms import bellman_ford_path

def test_bellman_ford_peso_negativo():
    g = Graph(directed=True, allow_negative_weights=True)
    g.add_node("1")
    g.add_node("2")
    g.add_node("3")
    
    g.add_edge("1", "2", peso=5)
    g.add_edge("2", "3", peso=-2)
    
    resultado = bellman_ford_path(g, "1", "3")
    assert resultado["custo"] == 3


def test_bellman_ford_ciclo_negativo():
    g = Graph(directed=True, allow_negative_weights=True)
    g.add_node("1")
    g.add_node("2")
    g.add_node("3")
    g.add_edge("1", "2", peso=1)
    g.add_edge("2", "3", peso=-5)
    g.add_edge("3", "1", peso=2) 
    
    with pytest.raises(ValueError):
        bellman_ford_path(g, "1", "3")