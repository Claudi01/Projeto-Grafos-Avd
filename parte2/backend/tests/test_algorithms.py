import pytest
from src.graphs.graph import Graph
from src.graphs.algorithms import bfs_layers, dfs, dijkstra, bellman_ford_path

@pytest.fixture
def grafo_pequeno():
    """Cria um grafo pequeno de testes sem precisar carregar o CSV gigante."""
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
    """Testa se o BFS mapeia os níveis/camadas corretamente em um grafo pequeno."""
    niveis = bfs_layers(grafo_pequeno, "A")
    
    assert niveis["A"] == 0
    assert niveis["B"] == 1 
    assert niveis["C"] == 1 
    assert niveis["D"] == 2 

def test_dfs_visita_todos(grafo_pequeno):
    """Testa se o DFS atinge a profundidade e lista os nós visitados."""
    visitados = dfs(grafo_pequeno, "A")
    
    assert "A" in visitados
    assert "D" in visitados
    assert len(visitados) == 4

def test_dijkstra_recusa_peso_negativo():
    """Testa se o Dijkstra levanta erro ao encontrar peso negativo."""
    g = Graph(directed=False, allow_negative_weights=True)
    g.add_node("X")
    g.add_node("Y")
    g.add_edge("X", "Y", peso=-5)
    
    with pytest.raises(ValueError):
        dijkstra(g, "X", "Y")

def test_bellman_ford_peso_negativo():
    """Testa Bellman-Ford suportando peso negativo sem ciclo."""
    g = Graph(directed=True, allow_negative_weights=True)
    g.add_node("1")
    g.add_node("2")
    g.add_node("3")
    
    g.add_edge("1", "2", peso=5)
    g.add_edge("2", "3", peso=-2)
    
    resultado = bellman_ford_path(g, "1", "3")
    assert resultado["custo"] == 3 # 5 - 2 = 3

def test_bellman_ford_ciclo_negativo():
    """Testa se o Bellman-Ford detecta e flagra um ciclo negativo."""
    g = Graph(directed=True, allow_negative_weights=True)
    g.add_node("1")
    g.add_node("2")
    g.add_node("3")
    g.add_edge("1", "2", peso=1)
    g.add_edge("2", "3", peso=-5)
    g.add_edge("3", "1", peso=2) 
    
    with pytest.raises(ValueError):
        bellman_ford_path(g, "1", "3")