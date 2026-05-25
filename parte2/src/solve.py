import time
import json
import random
from pathlib import Path
import sys
sys.setrecursionlimit(100000)

# Importando as estruturas da sua equipe
from src.graphs.io import build_tmdb_graph
from src.graphs.graph import Graph
from src.graphs.algorithms import (
    bfs_layers, 
    dfs, 
    dijkstra, 
    bellman_ford
)

def measure_time(func, *args, **kwargs):
    """Executa uma função e retorna o tempo em milissegundos e o resultado."""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    return (end - start) * 1000, result

def criar_cenarios_bellman_ford():
    """
    Gera dois subgrafos direcionados para provar o funcionamento do Bellman-Ford.
    """
    # Cenário 1: Peso negativo SEM ciclo negativo
    g_sem_ciclo = Graph(directed=True, allow_negative_weights=True)
    g_sem_ciclo.add_edge("A_Keanu Reeves", "M_The Matrix", peso=-5.0)
    g_sem_ciclo.add_edge("M_The Matrix", "A_Carrie-Anne Moss", peso=2.0)
    
    # Cenário 2: Com ciclo negativo detectável
    g_com_ciclo = Graph(directed=True, allow_negative_weights=True)
    g_com_ciclo.add_edge("A_Brad Pitt", "M_Fight Club", peso=1.0)
    g_com_ciclo.add_edge("M_Fight Club", "A_Edward Norton", peso=1.0)
    # Aresta de volta criando o ciclo negativo de soma -8
    g_com_ciclo.add_edge("A_Edward Norton", "A_Brad Pitt", peso=-10.0) 

    return g_sem_ciclo, g_com_ciclo

def run_parte2(csv_path: str, max_edges: int = 100000):
    report = {
        "dataset_info": {},
        "bfs_performance": [],
        "dfs_performance": [],
        "dijkstra_performance": [],
        "bellman_ford_performance": {}
    }

    # 1. Carregamento do Grafo Principal
    print("\n[1/5] Construindo o Grafo Bipartido TMDB...")
    t_build, graph = measure_time(build_tmdb_graph, csv_path, max_edges)
    
    atores = [n for n in graph.nodes() if n.startswith("A_")]
    filmes = [n for n in graph.nodes() if n.startswith("M_")]
    
    report["dataset_info"] = {
        "ordem": graph.order(),
        "tamanho": graph.size(),
        "tempo_construcao_ms": round(t_build, 2),
        "total_atores": len(atores),
        "total_filmes": len(filmes)
    }
    print(f"Grafo carregado! {graph.order()} nós e {graph.size()} arestas.")

    # Escolher 3 fontes aleatórias garantidas de existir para BFS/DFS
    fontes_busca = random.sample(atores, 3)

    # 2. Executando BFS
    print("\n[2/5] Executando BFS a partir de 3 fontes...")
    for fonte in fontes_busca:
        t_bfs, layers = measure_time(bfs_layers, graph, fonte)
        report["bfs_performance"].append({
            "fonte": fonte,
            "tempo_ms": round(t_bfs, 2),
            "nos_alcancados": len(layers),
            "camada_maxima": max(layers.values()) if layers else 0
        })

    # 3. Executando DFS
    print("\n[3/5] Executando DFS a partir das mesmas 3 fontes...")
    for fonte in fontes_busca:
        t_dfs, ordem = measure_time(dfs, graph, fonte)
        report["dfs_performance"].append({
            "fonte": fonte,
            "tempo_ms": round(t_dfs, 2),
            "nos_visitados": len(ordem)
        })

    # 4. Executando Dijkstra (5 pares aleatórios)
    print("\n[4/5] Executando Dijkstra para 5 pares Origem-Destino...")
    pares_dijkstra = []
    for _ in range(5):
        origem = random.choice(atores)
        destino = random.choice(atores)
        pares_dijkstra.append((origem, destino))

    for origem, destino in pares_dijkstra:
        try:
            t_dijk, result = measure_time(dijkstra, graph, origem, destino)
            custo = result["custo"]
            caminho_len = len(result["caminho"])
        except Exception as e:
            t_dijk, custo, caminho_len = 0, str(e), 0

        report["dijkstra_performance"].append({
            "origem": origem,
            "destino": destino,
            "tempo_ms": round(t_dijk, 2),
            "custo": custo,
            "tamanho_caminho": caminho_len
        })

    # 5. Executando Bellman-Ford
    print("\n[5/5] Testando cenários do Bellman-Ford...")
    g_sem_ciclo, g_com_ciclo = criar_cenarios_bellman_ford()
    
    # Teste A: Sem ciclo
    t_bf_ok, bf_ok_result = measure_time(bellman_ford, g_sem_ciclo, "A_Keanu Reeves")
    report["bellman_ford_performance"]["cenario_sem_ciclo"] = {
        "tempo_ms": round(t_bf_ok, 2),
        "status": "Sucesso",
        "distancia_final": bf_ok_result["distancias"]["A_Carrie-Anne Moss"]
    }

    # Teste B: Com ciclo
    try:
        t_bf_erro, _ = measure_time(bellman_ford, g_com_ciclo, "A_Brad Pitt")
        status = "Falha - O erro não foi disparado!"
    except ValueError as e:
        status = "Ciclo negativo detectado"
        t_bf_erro = 0 # Ignorar tempo se deu erro

    report["bellman_ford_performance"]["cenario_com_ciclo_negativo"] = {
        "status": status
    }

    # Salvar Relatório
    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)
    report_path = out_dir / "parte2_report.json"
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    print(f"\nConcluído! Relatório gerado em: {report_path}")

if __name__ == "__main__":
    CSV_TMDB = "data/tmdb_5000_credits.csv"
    run_parte2(CSV_TMDB, max_edges=100000)