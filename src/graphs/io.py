import pandas as pd
import ast
import json

REGIOES_VALIDAS = {
    "Norte",
    "Nordeste",
    "Centro-Oeste",
    "Sudeste",
    "Sul"
}


def load_airports(path: str) -> pd.DataFrame:
    """
    Carrega o CSV de aeroportos.
    Espera as colunas: iata, cidade, regiao.
    """
    df = pd.read_csv(path)
    return df


def normalize_airports(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza os dados dos aeroportos:
    - padroniza nomes das colunas;
    - remove espaços;
    - coloca IATA em maiúsculo;
    - padroniza nomes das regiões.
    """

    df = df.copy()
    df.columns = [col.strip().lower() for col in df.columns]

    required_columns = {"iata", "cidade", "regiao"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")

  
    df["iata"] = df["iata"].astype(str).str.strip().str.upper()
    df["cidade"] = df["cidade"].astype(str).str.strip()
    df["regiao"] = df["regiao"].astype(str).str.strip()

    
    mapa_regioes = {
        "norte": "Norte",
        "nordeste": "Nordeste",
        "centro-oeste": "Centro-Oeste",
        "centro oeste": "Centro-Oeste",
        "sudeste": "Sudeste",
        "sul": "Sul"
    }

    df["regiao"] = df["regiao"].str.lower().map(mapa_regioes)

    return df


def validate_airports(df: pd.DataFrame) -> None:
    """
    Valida se a base de aeroportos está adequada para construção do grafo.
    """

    if df[["iata", "cidade", "regiao"]].isnull().any().any():
        raise ValueError("Existem campos vazios em iata, cidade ou regiao.")

    invalid_iata = df[~df["iata"].str.match(r"^[A-Z]{3}$")]

    if not invalid_iata.empty:
        raise ValueError(
            f"Códigos IATA inválidos encontrados: {invalid_iata['iata'].tolist()}"
        )

    duplicated = df[df["iata"].duplicated()]["iata"].tolist()

    if duplicated:
        raise ValueError(f"Códigos IATA duplicados encontrados: {duplicated}")

    invalid_regions = set(df["regiao"]) - REGIOES_VALIDAS

    if invalid_regions:
        raise ValueError(f"Regiões inválidas encontradas: {invalid_regions}")


def get_airport_nodes(df: pd.DataFrame) -> dict:
    """
    Transforma o DataFrame em um dicionário de nós do grafo.

    Exemplo de retorno:
    {
        "REC": {"cidade": "Recife", "regiao": "Nordeste"},
        "GRU": {"cidade": "São Paulo", "regiao": "Sudeste"}
    }
    """

    nodes = {}

    for _, row in df.iterrows():
        iata = row["iata"]

        nodes[iata] = {
            "cidade": row["cidade"],
            "regiao": row["regiao"]
        }

    return nodes


def load_normalized_airports(path: str) -> pd.DataFrame:
    """
    Função principal da etapa de normalização.
    Carrega, normaliza e valida os aeroportos.
    """

    df = load_airports(path)
    df = normalize_airports(df)
    validate_airports(df)

    return df
def load_adjacencies(path: str) -> pd.DataFrame:
    """
    Carrega o CSV de adjacências.

    Espera as colunas:
    origem, destino, tipo_conexao, justificativa, peso
    """

    df = pd.read_csv(path)
    return df


def normalize_adjacencies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza o CSV de adjacências.
    """

    df = df.copy()
    df.columns = [col.strip().lower() for col in df.columns]

    required_columns = {
        "origem",
        "destino",
        "tipo_conexao",
        "justificativa",
        "peso"
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes em adjacências: {missing}")

    df["origem"] = df["origem"].astype(str).str.strip().str.upper()
    df["destino"] = df["destino"].astype(str).str.strip().str.upper()
    df["tipo_conexao"] = df["tipo_conexao"].astype(str).str.strip()
    df["justificativa"] = df["justificativa"].astype(str).str.strip()
    df["peso"] = df["peso"].astype(float)

    return df


def validate_adjacencies(df_edges: pd.DataFrame, df_airports: pd.DataFrame) -> None:
    """
    Valida se as arestas estão corretas.

    Regras:
    - origem e destino precisam existir no CSV de aeroportos;
    - não pode haver origem igual ao destino;
    - peso não pode ser negativo;
    - não pode haver aresta duplicada no grafo não direcionado.
    """

    aeroportos_validos = set(df_airports["iata"])

    # Verifica campos vazios
    if df_edges[["origem", "destino", "tipo_conexao", "justificativa", "peso"]].isnull().any().any():
        raise ValueError("Existem campos vazios no arquivo de adjacências.")

    # Verifica se origem existe
    origens_invalidas = set(df_edges["origem"]) - aeroportos_validos

    if origens_invalidas:
        raise ValueError(f"Origens inválidas encontradas: {origens_invalidas}")

    # Verifica se destino existe
    destinos_invalidos = set(df_edges["destino"]) - aeroportos_validos

    if destinos_invalidos:
        raise ValueError(f"Destinos inválidos encontrados: {destinos_invalidos}")

    # Verifica origem igual ao destino
    loops = df_edges[df_edges["origem"] == df_edges["destino"]]

    if not loops.empty:
        raise ValueError(
            f"Existem arestas com origem igual ao destino: {loops[['origem', 'destino']].values.tolist()}"
        )

    # Verifica pesos negativos
    pesos_negativos = df_edges[df_edges["peso"] < 0]

    if not pesos_negativos.empty:
        raise ValueError("Existem pesos negativos em adjacencias_aeroportos.csv.")

    # Verifica arestas duplicadas considerando grafo não direcionado
    pares = set()

    for _, row in df_edges.iterrows():
        par = tuple(sorted([row["origem"], row["destino"]]))

        if par in pares:
            raise ValueError(f"Aresta duplicada encontrada: {par}")

        pares.add(par)


def load_normalized_adjacencies(path_edges: str, df_airports: pd.DataFrame) -> pd.DataFrame:
    """
    Carrega, normaliza e valida as adjacências.
    """

    df_edges = load_adjacencies(path_edges)
    df_edges = normalize_adjacencies(df_edges)
    validate_adjacencies(df_edges, df_airports)

    return df_edges


def build_airport_graph(path_airports: str, path_edges: str):
    """
    Cria o grafo completo a partir dos arquivos:

    - data/aeroportos_data.csv
    - data/adjacencias_aeroportos.csv
    """

    from src.graphs.graph import Graph

    df_airports = load_normalized_airports(path_airports)
    df_edges = load_normalized_adjacencies(path_edges, df_airports)

    graph = Graph(directed=False)

    # Adiciona os aeroportos como nós
    for _, row in df_airports.iterrows():
        graph.add_node(
            row["iata"],
            cidade=row["cidade"],
            regiao=row["regiao"]
        )

    # Adiciona as conexões como arestas
    for _, row in df_edges.iterrows():
        graph.add_edge(
            row["origem"],
            row["destino"],
            peso=row["peso"],
            tipo_conexao=row["tipo_conexao"],
            justificativa=row["justificativa"]
        )

    return graph

#PARTE 2

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