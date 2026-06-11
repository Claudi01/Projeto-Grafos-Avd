import pandas as pd
import json
import ast
from collections import defaultdict
from src.graphs.graph import Graph

TOP_K = 10  # peso max

def build_tmdb_graph(path_tmdb: str, threshold: int = 1, max_edges: int = 200000): 
    df = pd.read_csv(path_tmdb)

    if 'title' not in df.columns or 'cast' not in df.columns or 'movie_id' not in df.columns:
        raise ValueError("O dataset precisa conter as colunas 'movie_id', 'title' e 'cast'.")

    graph = Graph(directed=False)

    actor_movies = defaultdict(list)
    movie_titles = {}

    print("Lendo CSV e mapeando nós...")
    for index, row in df.iterrows():
        movie_id = row['movie_id']
        title = row['title']
        cast_str = str(row['cast'])

        movie_id_str = str(movie_id)
        graph.add_node(movie_id_str, title=title, tipo="filme")
        movie_titles[movie_id_str] = title

        if cast_str == "nan" or not cast_str.strip():
            continue

        try:
            try:
                cast_data = json.loads(cast_str.replace("'", '"'))
            except json.JSONDecodeError:
                cast_data = ast.literal_eval(cast_str)
        except (ValueError, SyntaxError):
            continue

        if not isinstance(cast_data, list):
            continue

        for actor in cast_data[:TOP_K]:  
            if isinstance(actor, dict) and 'name' in actor:
                actor_name = str(actor['name']).strip()
                if actor_name:
                    actor_movies[actor_name].append(movie_id_str)

    # GRUDA O DICIONÁRIO DE TÍTULOS NO OBJETO GRAPH PARA O CLI ACESSAR SEM ERROS
    graph.movie_titles = movie_titles

    print("Calculando interseções e construindo arestas...")
    movie_pair_counts = defaultdict(lambda: defaultdict(int))

    for actor, movies in actor_movies.items():
        for i in range(len(movies)):
            for j in range(i + 1, len(movies)):
                m1, m2 = movies[i], movies[j]
                if m1 != m2:
                    u, v = min(m1, m2), max(m1, m2)
                    movie_pair_counts[u][v] += 1

    edges_added = 0
    for u, neighbors in movie_pair_counts.items():
        for v, shared_actors in neighbors.items():
            if shared_actors >= threshold:
                
                # TRAVA DE SEGURANÇA: LIMITE DE 200 MIL ARESTAS
                if edges_added >= max_edges:
                    break
                    
                peso = shared_actors  
                graph.add_edge(
                    u, v, 
                    peso=peso, 
                    atores_em_comum=shared_actors, 
                    tipo_conexao="elenco_compartilhado"
                )
                edges_added += 1
                
        if edges_added >= max_edges:
            print(f"⚠️ Limite máximo de segurança ({max_edges} arestas) atingido!")
            break

    print(f"Grafo construído com sucesso: {graph.order()} nós e {graph.size()} arestas.")
    return graph