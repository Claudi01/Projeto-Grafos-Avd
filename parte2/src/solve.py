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
    g_sem_ciclo.add_edge("Keanu Reeves", "Carrie-Anne Moss", peso=-5.0)
    g_sem_ciclo.add_edge("Carrie-Anne Moss", "Laurence Fishburne", peso=2.0)
    
    g_com_ciclo = Graph(directed=True, allow_negative_weights=True)
    g_com_ciclo.add_edge("Brad Pitt", "Edward Norton", peso=1.0)
    g_com_ciclo.add_edge("Edward Norton", "Helena Bonham Carter", peso=1.0)
    g_com_ciclo.add_edge("Helena Bonham Carter", "Brad Pitt", peso=-10.0) 

    return g_sem_ciclo, g_com_ciclo

def run_parte2(csv_path: str, max_edges: int = 100000):
    report = {
        "dataset_info": {},
        "bfs": [],
        "dfs": [],
        "dijkstra": [],
        "bellman_ford": {}
    }

    t_build, graph = measure_time(build_tmdb_graph, csv_path, max_edges)
    
    atores = graph.nodes()
    
    report["dataset_info"] = {
        "ordem": graph.order(),
        "tamanho": graph.size(),
        "tempo_construcao_ms": round(t_build, 2),
        "total_atores": len(atores)
    }

    fontes_busca = random.sample(atores, min(3, len(atores)))

    for fonte in fontes_busca:
        t_bfs, layers = measure_time(bfs_layers, graph, fonte)
        report["bfs"].append({
            "fonte": fonte,
            "tempo_ms": round(t_bfs, 2),
            "nos_alcancados": len(layers),
            "camada_maxima": max(layers.values()) if layers else 0
        })

    for fonte in fontes_busca:
        t_dfs, ordem = measure_time(dfs, graph, fonte)
        report["dfs"].append({
            "fonte": fonte,
            "tempo_ms": round(t_dfs, 2),
            "nos_visitados": len(ordem)
        })

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
            
            if custo == float('inf'):
                custo = "Infinito (Sem caminho)"
                
        except Exception as e:
            t_dijk, custo, caminho_len = 0, str(e), 0

        report["dijkstra"].append({
            "origem": origem,
            "destino": destino,
            "tempo_ms": round(t_dijk, 2),
            "custo": custo,
            "tamanho_caminho": caminho_len
        })

    g_sem_ciclo, g_com_ciclo = criar_cenarios_bellman_ford()
    
    t_bf_ok, bf_ok_result = measure_time(bellman_ford, g_sem_ciclo, "Keanu Reeves")
    report["bellman_ford"]["cenario_sem_ciclo"] = {
        "tempo_ms": round(t_bf_ok, 2),
        "status": "Sucesso",
        "distancia_final": bf_ok_result["distancias"].get("Laurence Fishburne", 0)
    }

    try:
        t_bf_erro, _ = measure_time(bellman_ford, g_com_ciclo, "Brad Pitt")
        status = "Falha - O erro não foi disparado!"
    except ValueError:
        status = "Ciclo negativo detectado com sucesso" 

    report["bellman_ford"]["cenario_com_ciclo_negativo"] = {
        "status": status
    }

    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)
    report_path = out_dir / "parte2_report.json"
    
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    print(f"Processamento concluído! Relatório gerado em: {report_path}")

if __name__ == "__main__":
    CSV_TMDB = "data/tmdb_5000_credits.csv"
    run_parte2(CSV_TMDB, max_edges=100000)