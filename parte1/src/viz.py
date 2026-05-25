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


if __name__ == "__main__":
    os.makedirs("out", exist_ok=True)
    
    # Executa todas as 4 visualizações analíticas obrigatórias
    plot_degree_histogram("out/graus.csv", "out/histograma_graus.png")
    plot_top_airports("out/graus.csv", "out/ranking_graus.png")
    plot_region_density("out/regioes.json", "out/densidade_regioes.png")
    plot_ego_density("out/ego_aeroportos.csv", "out/histograma_ego_densidade.png")