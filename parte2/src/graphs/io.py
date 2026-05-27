import pandas as pd
import ast
import json

def build_tmdb_graph(path_tmdb: str, max_edges: int = 200000, top_cast: int = 5):
    from src.graphs.graph import Graph
    import pandas as pd
    import json
    import ast

    df = pd.read_csv(path_tmdb)

    if 'title' not in df.columns or 'cast' not in df.columns:
        raise ValueError("O dataset do TMDB precisa conter as colunas 'title' e 'cast'.")

    graph = Graph(directed=False)
    edges_added = 0

    for index, row in df.iterrows():
        if edges_added >= max_edges:
            break

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

        atores_filme = []
        for actor in cast_data:
            if isinstance(actor, dict) and 'name' in actor:
                actor_name = str(actor['name']).strip()
                if actor_name:
                    if actor_name not in atores_filme:
                        atores_filme.append(actor_name)
            if len(atores_filme) == top_cast:
                break

        for ator in atores_filme:
            graph.add_node(ator, tipo="ator", nome=ator)

        for i in range(len(atores_filme)):
            for j in range(i + 1, len(atores_filme)):
                ator_u = atores_filme[i]
                ator_v = atores_filme[j]

                if ator_u == ator_v:
                    continue

                if graph.has_edge(ator_u, ator_v):
                    peso_atual = graph.get_edge_attrs(ator_u, ator_v)["peso"]
                    graph.add_edge(ator_u, ator_v, peso=peso_atual + 1.0, tipo_conexao="colaboracao")
                else:
                    graph.add_edge(ator_u, ator_v, peso=1.0, tipo_conexao="colaboracao")
                    edges_added += 1

                if edges_added >= max_edges:
                    break
            if edges_added >= max_edges:
                break

    return graph