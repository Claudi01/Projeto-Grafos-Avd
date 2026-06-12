import pytest
from src.graphs.graph import Graph
from src.graphs.algorithms import dijkstra

def test_dijkstra_recusa_peso_negativo():
    g = Graph(directed=False, allow_negative_weights=True)
    g.add_node("X")
    g.add_node("Y")
    g.add_edge("X", "Y", peso=-5)
    
    with pytest.raises(ValueError):
        dijkstra(g, "X", "Y")