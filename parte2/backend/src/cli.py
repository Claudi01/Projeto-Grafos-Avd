import argparse
import sys
import time
import json
from pathlib import Path
from src.graphs.io import build_tmdb_graph
from src.graphs.algorithms import bfs_layers, dfs, dijkstra, bellman_ford_path

sys.setrecursionlimit(100000)

def encontrar_id_por_titulo(graph, titulo):
    if hasattr(graph, 'movie_titles'):
        for movie_id, title in graph.movie_titles.items():
            if str(title).lower() == titulo.lower():
                return movie_id
    return None

def main():
    parser = argparse.ArgumentParser(description="CLI para Algoritmos em Grafos")
    parser.add_argument("--dataset", type=str, default="data/tmdb_5000_credits.csv")
    parser.add_argument("--threshold", type=int, default=1)
    parser.add_argument("--max_edges", type=int, default=200000)
    parser.add_argument("--algoritmo", type=str, required=True, choices=["bfs", "dfs", "dijkstra", "bellman-ford", "BELLMAN-FORD", "DIJKSTRA", "BFS", "DFS"])
    parser.add_argument("--origem", type=str, required=True)
    parser.add_argument("--destino", type=str)
    
    # NOVO: Argumento exigido pela professora para salvar a saída
    parser.add_argument("--out", type=str, help="Diretório de saída para salvar o resultado")

    args = parser.parse_args()
    algoritmo_escolhido = args.algoritmo.lower()

    if algoritmo_escolhido in ["dijkstra", "bellman-ford"] and not args.destino:
        print("Erro: O algoritmo selecionado exige o argumento --destino.")
        sys.exit(1)

    print(f"Carregando dataset e construindo o grafo...")
    start_time = time.perf_counter()
    graph = build_tmdb_graph(args.dataset, threshold=args.threshold, max_edges=args.max_edges)
    end_time = time.perf_counter()
    print(f"Grafo construido em {end_time - start_time:.2f} s. Ordem: {graph.order()} | Tamanho: {graph.size()}\n")

    origem_id = args.origem
    if not graph.has_node(origem_id):
        possivel_id = encontrar_id_por_titulo(graph, args.origem)
        if possivel_id:
            origem_id = possivel_id
        else:
            print(f"Erro: Origem '{args.origem}' não encontrada.")
            sys.exit(1)

    destino_id = args.destino
    if args.destino:
        if not graph.has_node(destino_id):
            possivel_id = encontrar_id_por_titulo(graph, args.destino)
            if possivel_id:
                destino_id = possivel_id
            else:
                print(f"Erro: Destino '{args.destino}' não encontrado.")
                sys.exit(1)

    dados_saida = {
        "algoritmo": algoritmo_escolhido.upper(),
        "origem": origem_id,
        "destino": destino_id,
    }

    try:
        start_algo = time.perf_counter()
        
        if algoritmo_escolhido == "bfs":
            print(f"Executando BFS a partir de '{origem_id}'...")
            resultado = bfs_layers(graph, origem_id)
            dados_saida["nos_alcancados"] = len(resultado)
            dados_saida["camada_maxima"] = max(resultado.values()) if resultado else 0
            
        elif algoritmo_escolhido == "dfs":
            print(f"Executando DFS a partir de '{origem_id}'...")
            resultado = dfs(graph, origem_id)
            dados_saida["nos_visitados"] = len(resultado)
            dados_saida["primeiros_nos"] = resultado[:10]
            
        elif algoritmo_escolhido == "dijkstra":
            print(f"Executando Dijkstra de '{origem_id}' para '{destino_id}'...")
            resultado = dijkstra(graph, origem_id, destino_id)
            dados_saida["custo"] = resultado['custo']
            dados_saida["caminho"] = resultado['caminho']
            
        elif algoritmo_escolhido == "bellman-ford":
            print(f"Executando Bellman-Ford de '{origem_id}' para '{destino_id}'...")
            resultado = bellman_ford_path(graph, origem_id, destino_id)
            dados_saida["custo"] = resultado['custo']
            dados_saida["caminho"] = resultado['caminho']

        end_algo = time.perf_counter()
        dados_saida["tempo_execucao_ms"] = (end_algo - start_algo) * 1000

        print(json.dumps(dados_saida, indent=4, ensure_ascii=False))
        if args.out:
            out_dir = Path(args.out)
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / f"resultado_{algoritmo_escolhido}.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(dados_saida, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"\nErro na execução: {e}")

if __name__ == "__main__":
    main()