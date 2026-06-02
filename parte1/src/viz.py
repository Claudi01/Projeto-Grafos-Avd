import os
import json
import pandas as pd
import matplotlib.pyplot as plt

def plot_degree_histogram(path_in: str, path_out: str) -> None:
    """
    Gera um histograma da distribuição de graus dos aeroportos.
    """
    if not os.path.exists(path_in):
        raise FileNotFoundError(f"Arquivo base não encontrado: {path_in}")

    df = pd.read_csv(path_in)

    if "grau" not in df.columns:
        raise ValueError("O arquivo de graus não possui a coluna 'grau'.")

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(df["grau"], bins=10, color="skyblue", edgecolor="black")

    ax.set_title("Distribuição de Graus dos Aeroportos", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Grau (Número de conexões)", fontsize=12)
    ax.set_ylabel("Frequência (Quantidade de aeroportos)", fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    plt.tight_layout()
    plt.savefig(path_out, dpi=300)
    plt.close(fig)


def plot_top_airports(path_in: str, path_out: str, top_n: int = 10) -> None:
    """
    Gera um gráfico de barras com o ranking dos aeroportos mais conectados.
    """
    if not os.path.exists(path_in):
        raise FileNotFoundError(f"Arquivo base não encontrado: {path_in}")
    
    df = pd.read_csv(path_in)
    
    if "grau" not in df.columns or "aeroporto" not in df.columns:
        raise ValueError("O arquivo deve conter as colunas 'aeroporto' e 'grau'.")
    
    df_sorted = df.sort_values(by="grau", ascending=False).head(top_n)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_sorted["aeroporto"], df_sorted["grau"], color="coral", edgecolor="black")
    
    ax.set_title(f"Top {top_n} Aeroportos Mais Conectados", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Aeroportos (IATA)", fontsize=12)
    ax.set_ylabel("Grau (Número de conexões)", fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(path_out, dpi=300)
    plt.close(fig)


def plot_region_density(path_in: str, path_out: str) -> None:
    """
    Gera um gráfico de barras comparando a densidade interna das regiões.
    """
    if not os.path.exists(path_in):
        raise FileNotFoundError(f"Arquivo base não encontrado: {path_in}")
        
    with open(path_in, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Versão corrigida lendo o JSON como lista
    regioes = [item["regiao"] for item in data]
    densidades = [item["densidade"] for item in data]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(regioes, densidades, color="mediumseagreen", edgecolor="black")
    
    ax.set_title("Densidade do Grafo por Região", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Região", fontsize=12)
    ax.set_ylabel("Densidade", fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(path_out, dpi=300)
    plt.close(fig)


def plot_ego_density(path_in: str, path_out: str) -> None:
    """
    Gera um histograma da distribuição da densidade das ego-networks.
    """
    if not os.path.exists(path_in):
        raise FileNotFoundError(f"Arquivo base não encontrado: {path_in}")
        
    df = pd.read_csv(path_in)
    
    if "densidade_ego" not in df.columns:
        raise ValueError("O arquivo deve conter a coluna 'densidade_ego'.")
        
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(df["densidade_ego"], bins=10, color="orchid", edgecolor="black")
    
    ax.set_title("Distribuição da Densidade das Ego-Networks", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Densidade Ego", fontsize=12)
    ax.set_ylabel("Frequência (Quantidade de aeroportos)", fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(path_out, dpi=300)
    plt.close(fig)

def plot_avd_scatter(path_airports: str, path_degrees: str, path_passengers: str, path_out: str) -> None:
    """
    Gera um gráfico de dispersão cruzando o Grau do aeroporto com o Volume de Passageiros,
    aplicando Leis da Gestalt (Similaridade em cores, Proximidade em clusters).
    """
    if not os.path.exists(path_airports) or not os.path.exists(path_degrees) or not os.path.exists(path_passengers):
        print("Bases de AVD não encontradas. Verifique se passageiros.csv existe.")
        return

    df_airports = pd.read_csv(path_airports)
    df_degrees = pd.read_csv(path_degrees)
    df_passengers = pd.read_csv(path_passengers)

    df_merged = df_passengers.merge(df_airports[['iata', 'regiao']], on='iata', how='left')
    df_merged = df_merged.merge(df_degrees, left_on='iata', right_on='aeroporto', how='left').fillna(0)

    fig, ax = plt.subplots(figsize=(10, 7))
    cores_regioes = {'Norte': '#2ca02c', 'Nordeste': '#ff7f0e', 'Centro-Oeste': '#d62728', 'Sudeste': '#1f77b4', 'Sul': '#9467bd'}

    for regiao, cor in cores_regioes.items():
        df_subset = df_merged[df_merged['regiao'] == regiao]
        ax.scatter(df_subset['grau'], df_subset['passageiros_milhoes'],
                   s=df_subset['passageiros_milhoes'] * 20 + 50,
                   c=cor, label=regiao, alpha=0.8, edgecolors='w', linewidth=1.5)

    for _, row in df_merged.iterrows():
        ax.annotate(row['iata'], (row['grau'], row['passageiros_milhoes']),
                    textcoords="offset points", xytext=(7, 0), ha='left', fontsize=9)

    ax.set_title("Storytelling: Grau Estrutural vs. Volume de Passageiros", fontsize=15, fontweight="bold", pad=20)
    ax.set_xlabel("Grau (Quantidade de Conexões)", fontsize=12)
    ax.set_ylabel("Tráfego Anual (Milhões de Passageiros)", fontsize=12)
    ax.legend(title="Regiões (Gestalt: Similaridade)", bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, linestyle="--", alpha=0.4)
    
   
    fig.text(0.99, 0.01, 'Fonte dos Dados: ANAC', ha='right', va='bottom', fontsize=8, color='gray', style='italic')

    plt.tight_layout()
    plt.savefig(path_out, dpi=300)
    plt.close(fig)

if __name__ == "__main__":
    os.makedirs("parte1/out", exist_ok=True)
    
    # Executa todas as 4 visualizações 
    plot_degree_histogram("parte1/out/graus.csv", "parte1/out/histograma_graus.png")
    plot_top_airports("parte1/out/graus.csv", "parte1/out/ranking_graus.png")
    plot_region_density("parte1/out/regioes.json", "parte1/out/densidade_regioes.png")
    plot_ego_density("parte1/out/ego_aeroportos.csv", "parte1/out/histograma_ego_densidade.png")

    plot_ego_density("parte1/out/ego_aeroportos.csv", "parte1/out/histograma_ego_densidade.png")
    
    plot_avd_scatter(
        path_airports="parte1/data/aeroportos_data.csv",
        path_degrees="parte1/out/graus.csv",
        path_passengers="parte1/data/passageiros.csv",
        path_out="parte1/out/avd_passageiros_vs_conexoes.png"
    )