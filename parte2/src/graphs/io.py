import pandas as pd
import ast
import json

def build_tmdb_graph(path_tmdb: str, max_edges: int = 200000):
    """
    Cria o grafo bipartido (Filmes e Atores) a partir do dataset do TMDB.
    """
    from src.graphs.graph import Graph

    print(f"Lendo dataset do TMDB em: {path_tmdb}...")
    df = pd.read_csv(path_tmdb)

    if 'title' not in df.columns or 'cast' not in df.columns:
        raise ValueError("O dataset do TMDB precisa conter as colunas 'title' e 'cast'.")

    graph = Graph(directed=False)
    edges_added = 0

    print("Construindo o grafo de atores e filmes (Isso pode levar alguns segundos)...")
    
    for index, row in df.iterrows():
        if edges_added >= max_edges:
            break
            
        movie_title = str(row['title']).strip()
        if not movie_title or movie_title == "nan":
            continue
            
        movie_node = f"M_{movie_title}"
        graph.add_node(movie_node, tipo="filme", titulo=movie_title)
        
        cast_str = str(row['cast'])
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
            
        for actor in cast_data:
            if isinstance(actor, dict) and 'name' in actor:
                actor_name = str(actor['name']).strip()
                if not actor_name:
                    continue
                    
                actor_node = f"A_{actor_name}"
                graph.add_node(actor_node, tipo="ator", nome=actor_name)
                
                graph.add_edge(
                    movie_node, 
                    actor_node, 
                    peso=1.0, 
                    tipo_conexao="atuou_em"
                )
                edges_added += 1
                
                if edges_added >= max_edges:
                    break

    print(f"Grafo do TMDB construído! Total de arestas: {edges_added}")
    return graph