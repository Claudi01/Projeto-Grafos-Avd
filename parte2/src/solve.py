import time
import json
import random
import sys
from pathlib import Path

sys.setrecursionlimit(100000)

from src.graphs.io import build_tmdb_graph
from src.graphs.graph import Graph
from src.graphs.algorithms import (
    bfs_layers, 
    dfs, 
    dijkstra, 
    bellman_ford
)

def measure_time(func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    return (end - start) * 1000, result

def criar_cenarios_bellman_ford():
    g_sem_ciclo = Graph(directed=True, allow_negative_weights=True)
    g_sem_ciclo.add_edge("A_Keanu Reeves", "A_Carrie-Anne Moss", peso=-5.0)
    g_sem_ciclo.add_edge("A_Carrie-Anne Moss", "A_Laurence Fishburne", peso=2.0)
    
    g_com_ciclo = Graph(directed=True, allow_negative_weights=True)
    g_com_ciclo.add_edge("A_Brad Pitt", "A_Edward Norton", peso=1.0)
    g_com_ciclo.add_edge("A_Edward Norton", "A_Helena Bonham Carter", peso=1.0)
    g_com_ciclo.add_edge("A_Helena Bonham Carter", "A_Brad Pitt", peso=-10.0) 

    return g_sem_ciclo, g_com_ciclo

def run_parte2(csv_path: str, max_edges: int = 100000):
    report = {
        "dataset_info": {},
        "bfs_performance": [],
        "dfs_performance": [],
        "dijkstra_performance": [],
        "bellman_ford_performance": {}
    }

    print("\n[1/5] Construindo a Rede de Atores TMDB...")
    t_build, graph = measure_time(build_tmdb_graph, csv_path, max_edges)
    
    atores = graph.nodes()
    
    report["dataset_info"] = {
        "ordem": graph.order(),
        "tamanho": graph.size(),
        "tempo_construcao_ms": round(t_build, 2),
        "total_atores": len(atores)
    }
    print(f"Grafo carregado! {graph.order()} nós e {graph.size()} arestas.")

    fontes_busca = random.sample(atores, min(3, len(atores)))

    print("\n[2/5] Executando BFS a partir de 3 fontes...")
    for fonte in fontes_busca:
        t_bfs, layers = measure_time(bfs_layers, graph, fonte)
        report["bfs_performance"].append({
            "fonte": fonte,
            "tempo_ms": round(t_bfs, 2),
            "nos_alcancados": len(layers),
            "camada_maxima": max(layers.values()) if layers else 0
        })

    print("\n[3/5] Executando DFS a partir das mesmas 3 fontes...")
    for fonte in fontes_busca:
        t_dfs, ordem = measure_time(dfs, graph, fonte)
        report["dfs_performance"].append({
            "fonte": fonte,
            "tempo_ms": round(t_dfs, 2),
            "nos_visitados": len(ordem)
        })

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
            
            # --- ADIÇÃO PARA CORRIGIR O JSON ---
            if custo == float('inf'):
                custo = "Infinito"
            # -----------------------------------
            
        except Exception as e:
            t_dijk, custo, caminho_len = 0, str(e), 0

        report["dijkstra_performance"].append({
            "origem": origem,
            "destino": destino,
            "tempo_ms": round(t_dijk, 2),
            "custo": custo,
            "tamanho_caminho": caminho_len
        })

    print("\n[5/5] Testando cenários do Bellman-Ford...")
    g_sem_ciclo, g_com_ciclo = criar_cenarios_bellman_ford()
    
    t_bf_ok, bf_ok_result = measure_time(bellman_ford, g_sem_ciclo, "A_Keanu Reeves")
    report["bellman_ford_performance"]["cenario_sem_ciclo"] = {
        "tempo_ms": round(t_bf_ok, 2),
        "status": "Sucesso",
        "distancia_final": bf_ok_result["distancias"].get("A_Laurence Fishburne", 0)
    }

    try:
        t_bf_erro, _ = measure_time(bellman_ford, g_com_ciclo, "A_Brad Pitt")
        status = "Falha - O erro não foi disparado!"
    except ValueError:
        status = "Ciclo negativo detectado com sucesso" 

    report["bellman_ford_performance"]["cenario_com_ciclo_negativo"] = {
        "status": status
    }

    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)
    report_path = out_dir / "parte2_report.json"
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    print(f"\nConcluído! Relatório gerado em: {report_path}")

if __name__ == "__main__":
    CSV_TMDB = "data/tmdb_5000_credits.csv"
    run_parte2(CSV_TMDB, max_edges=100000)