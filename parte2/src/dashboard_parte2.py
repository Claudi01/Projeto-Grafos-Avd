import json
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "out"

st.set_page_config(
    page_title="Dashboard - Grafos e AVD (Parte 2)",
    layout="wide",
    initial_sidebar_state="expanded",
)

COR_ALGORITMOS = {
    "BFS": "#636EFA",
    "DFS": "#EF553B",
    "Dijkstra": "#00CC96",
    "Bellman-Ford": "#AB63FA",
}

CARREGADO = {"report": None, "grafo": None}


@st.cache_data
def carregar_report():
    path = OUT_DIR / "parte2_report.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def carregar_grafo_amostra():
    path = OUT_DIR / "grafo_amostra.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_pyvis_html(grafo_data, grau_min):
    from pyvis.network import Network

    nodes = grafo_data["nodes"]
    links = grafo_data["links"]

    # Calcular grau real (contagem em links)
    grau_map = {}
    for n in nodes:
        grau_map[n["id"]] = 0
    for link in links:
        s, t = link["source"], link["target"]
        if s in grau_map:
            grau_map[s] += 1
        if t in grau_map:
            grau_map[t] += 1

    # Filtrar por grau mínimo
    nos_filtrados = {n["id"] for n in nodes if grau_map.get(n["id"], 0) >= grau_min}

    if not nos_filtrados:
        return None

    links_filtrados = [
        l for l in links
        if l["source"] in nos_filtrados and l["target"] in nos_filtrados
    ]

    max_degree = max(grau_map.values()) if grau_map else 1

    net = Network(height="600px", width="100%", bgcolor="#1E1E1E", font_color="white")
    net.toggle_physics(False)
    net.set_options("""
    {
      "nodes": {
        "borderWidth": 1,
        "borderWidthSelected": 2,
        "font": {"size": 10}
      },
      "edges": {
        "color": {"color": "#555555", "highlight": "#AAAAAA"},
        "width": 0.5
      },
      "physics": {
        "stabilization": {"iterations": 50},
        "barnesHut": {"springLength": 120, "springConstant": 0.02}
      }
    }
    """)

    for n in nodes:
        nid = n["id"]
        if nid not in nos_filtrados:
            continue
        deg = grau_map.get(nid, 0)
        ratio = deg / max_degree if max_degree > 0 else 0
        # Nós hub: maior = mais vermelho e maior; menor = mais azul e menor
        r = int(50 + 205 * ratio)
        g = int(50 + 100 * (1 - ratio))
        b = int(200 - 150 * ratio)
        color = f"rgb({r},{g},{b})"
        size = 8 + 22 * ratio
        title = f"{nid}<br>Grau: {deg}"
        net.add_node(nid, label=nid, color=color, size=size, title=title)

    node_set = set(net.get_nodes())
    for link in links_filtrados:
        s, t = link["source"], link["target"]
        if s in node_set and t in node_set:
            net.add_edge(s, t, weight=link.get("peso", 1.0))

    try:
        html = net.generate_html()
        return html
    except Exception:
        return None


def aba_performance(report):
    st.header("Performance de Algoritmos")
    st.markdown("Gráficos comparativos dos tempos de execução dos algoritmos de busca e caminhos mínimos.")

    # BFS / DFS
    st.subheader("BFS e DFS")
    dfs_rows = []
    for entry in report.get("bfs", []):
        dfs_rows.append({
            "Fonte": entry["fonte"],
            "Algoritmo": "BFS",
            "Tempo (ms)": entry["tempo_ms"],
            "Nós Alcançados": entry.get("nos_alcancados", 0),
        })
    for entry in report.get("dfs", []):
        dfs_rows.append({
            "Fonte": entry["fonte"],
            "Algoritmo": "DFS",
            "Tempo (ms)": entry["tempo_ms"],
            "Nós Alcançados": entry.get("nos_visitados", 0),
        })
    if dfs_rows:
        df_bfs_dfs = pd.DataFrame(dfs_rows)
        fig_bfs_dfs = px.bar(
            df_bfs_dfs,
            x="Fonte",
            y="Tempo (ms)",
            color="Algoritmo",
            barmode="group",
            color_discrete_map=COR_ALGORITMOS,
            title="BFS vs DFS — Tempo por Fonte",
        )
        fig_bfs_dfs.update_layout(
            yaxis_title="Tempo (ms)",
            xaxis_title="Vértice Fonte",
            legend_title="Algoritmo",
            hovermode="x unified",
        )
        st.plotly_chart(fig_bfs_dfs, use_container_width=True)

    # Dijkstra
    st.subheader("Dijkstra")
    dij_rows = report.get("dijkstra", [])
    if dij_rows:
        df_dij = pd.DataFrame(dij_rows)
        fig_dij = px.bar(
            df_dij,
            x="origem",
            y="tempo_ms",
            color=[COR_ALGORITMOS["Dijkstra"]] * len(df_dij),
            labels={"origem": "Origem", "tempo_ms": "Tempo (ms)"},
            title="Dijkstra — Tempo por Par (Origem → Destino)",
            hover_data=["destino", "custo", "tamanho_caminho"],
        )
        fig_dij.update_layout(
            showlegend=False,
            yaxis_title="Tempo (ms)",
            hovermode="x unified",
        )
        st.plotly_chart(fig_dij, use_container_width=True)

    # Bellman-Ford
    st.subheader("Bellman-Ford")
    bf = report.get("bellman_ford", {})
    bf_rows = []
    for cenario, dados in bf.items():
        bf_rows.append({
            "Cenário": cenario,
            "Tempo (ms)": dados.get("tempo_ms", 0),
            "Status": dados.get("status", ""),
        })
    if bf_rows:
        df_bf = pd.DataFrame(bf_rows)
        fig_bf = px.bar(
            df_bf,
            x="Cenário",
            y="Tempo (ms)",
            color=[COR_ALGORITMOS["Bellman-Ford"]] * len(df_bf),
            title="Bellman-Ford — Tempo por Cenário",
            hover_data=["Status"],
        )
        fig_bf.update_layout(showlegend=False, yaxis_title="Tempo (ms)")
        st.plotly_chart(fig_bf, use_container_width=True)

    # Visão geral: média de tempo por algoritmo
    st.subheader("Visão Geral — Média de Tempo por Algoritmo")
    medias = []
    if report.get("bfs"):
        medias.append({"Algoritmo": "BFS", "Média (ms)": round(
            sum(e["tempo_ms"] for e in report["bfs"]) / len(report["bfs"]), 2
        )})
    if report.get("dfs"):
        medias.append({"Algoritmo": "DFS", "Média (ms)": round(
            sum(e["tempo_ms"] for e in report["dfs"]) / len(report["dfs"]), 2
        )})
    if report.get("dijkstra"):
        medias.append({"Algoritmo": "Dijkstra", "Média (ms)": round(
            sum(e["tempo_ms"] for e in report["dijkstra"]) / len(report["dijkstra"]), 2
        )})
    for cenario, dados in bf.items():
        if "tempo_ms" in dados:
            medias.append({"Algoritmo": "Bellman-Ford", "Média (ms)": dados["tempo_ms"]})

    if medias:
        df_medias = pd.DataFrame(medias)
        fig_medias = px.bar(
            df_medias,
            x="Algoritmo",
            y="Média (ms)",
            color="Algoritmo",
            color_discrete_map=COR_ALGORITMOS,
            title="Média de Tempo de Execução por Algoritmo",
            text_auto=".2f",
        )
        fig_medias.update_layout(
            yaxis_title="Tempo médio (ms)",
            showlegend=False,
        )
        st.plotly_chart(fig_medias, use_container_width=True)

    # Info do dataset
    with st.expander("Informações do Dataset"):
        di = report.get("dataset_info", {})
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Ordem (nós)", di.get("ordem", "-"))
        col2.metric("Tamanho (arestas)", di.get("tamanho", "-"))
        col3.metric("Total de Atores", di.get("total_atores", "-"))
        col4.metric("Tempo de Construção (ms)", di.get("tempo_construcao_ms", "-"))


def aba_exploracao(grafo_data):
    st.header("Exploração do Grafo")
    st.markdown("Visualização interativa do subgrafo amostrado da rede de colaboração do TMDB.")

    nodes = grafo_data["nodes"]
    links = grafo_data["links"]

    # Painéis de métricas
    grau_map = {}
    for n in nodes:
        grau_map[n["id"]] = 0
    for link in links:
        s, t = link["source"], link["target"]
        if s in grau_map:
            grau_map[s] += 1
        if t in grau_map:
            grau_map[t] += 1

    max_degree = max(grau_map.values()) if grau_map else 0
    hubs = sum(1 for v in grau_map.values() if v > max_degree * 0.7) if max_degree > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ordem", len(nodes))
    col2.metric("Tamanho", len(links))
    col3.metric("Grau Máximo", max_degree)
    col4.metric("Hubs (≥70% máx)", hubs)

    # Slider de filtro na sidebar
    grau_min = st.sidebar.slider(
        "Grau mínimo dos nós",
        min_value=0,
        max_value=max_degree,
        value=0,
        help="Filtra nós com grau abaixo do valor selecionado.",
    )

    html = build_pyvis_html(grafo_data, grau_min)
    if html is None:
        st.warning("Nenhum nó encontrado com o filtro de grau selecionado.")
        return

    st.components.v1.html(html, height=650, scrolling=True)


def main():
    st.sidebar.title("Navegação")
    aba = st.sidebar.radio(
        "Selecione a aba:",
        ["Performance de Algoritmos", "Exploração do Grafo"],
        label_visibility="collapsed",
    )

    with st.sidebar:
        st.divider()
        report = carregar_report()
        grafo = carregar_grafo_amostra()

        if report:
            st.success("Relatório de performance carregado.")
        else:
            st.error("parte2_report.json não encontrado. Execute solve.py primeiro.")

        if grafo:
            st.success(f"Grafo amostra carregado ({len(grafo['nodes'])} nós).")
        else:
            st.error("grafo_amostra.json não encontrado. Execute solve.py primeiro.")

    if aba == "Performance de Algoritmos":
        if report:
            aba_performance(report)
        else:
            st.warning("Nenhum relatório disponível. Execute `solve.py` para gerar os dados.")
    elif aba == "Exploração do Grafo":
        if grafo:
            aba_exploracao(grafo)
        else:
            st.warning("Nenhum grafo amostra disponível. Execute `solve.py` para gerar os dados.")


if __name__ == "__main__":
    main()