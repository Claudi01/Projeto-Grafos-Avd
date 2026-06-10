from pathlib import Path
import json

import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from src.graphs.io import build_airport_graph
from src.graphs.algorithms import dijkstra


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
OUT_DIR = BASE_DIR / "out"
FRONTEND_DIR = BASE_DIR / "frontend"

AIRPORTS_PATH = DATA_DIR / "aeroportos_data.csv"
ADJACENCIES_PATH = DATA_DIR / "adjacencias_aeroportos.csv"
ROTAS_PATH = DATA_DIR / "rotas.csv"

GLOBAL_PATH = OUT_DIR / "global.json"
REGIOES_PATH = OUT_DIR / "regioes.json"
GRAUS_PATH = OUT_DIR / "graus.csv"
EGO_PATH = OUT_DIR / "ego_aeroportos.csv"
DISTANCIAS_PATH = OUT_DIR / "distancias_rotas.csv"
PASSENGERS_PATH = DATA_DIR / "passageiros.csv"

AIRPORT_COORDS = {
    "REC": {"lat": -8.1268, "lon": -34.9230},
    "SSA": {"lat": -12.9086, "lon": -38.3225},
    "FOR": {"lat": -3.7763, "lon": -38.5326},
    "NAT": {"lat": -5.9114, "lon": -35.2477},
    "JPA": {"lat": -7.1458, "lon": -34.9486},
    "GRU": {"lat": -23.4356, "lon": -46.4731},
    "CGH": {"lat": -23.6267, "lon": -46.6554},
    "GIG": {"lat": -22.8099, "lon": -43.2506},
    "CNF": {"lat": -19.6244, "lon": -43.9719},
    "VIX": {"lat": -20.2581, "lon": -40.2864},
    "BSB": {"lat": -15.8697, "lon": -47.9208},
    "GYN": {"lat": -16.6320, "lon": -49.2207},
    "CWB": {"lat": -25.5285, "lon": -49.1758},
    "FLN": {"lat": -27.6703, "lon": -48.5525},
    "POA": {"lat": -29.9944, "lon": -51.1714},
    "MAO": {"lat": -3.0386, "lon": -60.0497},
    "BEL": {"lat": -1.3793, "lon": -48.4763},
    "PVH": {"lat": -8.7093, "lon": -63.9023},
    "RBR": {"lat": -9.8689, "lon": -67.8981},
    "THE": {"lat": -5.0603, "lon": -42.8245},
}


app = Flask(__name__)
CORS(app)

def read_passengers_df():
    if not PASSENGERS_PATH.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {PASSENGERS_PATH}")

    df = pd.read_csv(PASSENGERS_PATH)

    if "iata" not in df.columns or "passageiros_milhoes" not in df.columns:
        raise ValueError(
            "O arquivo passageiros.csv deve conter as colunas: iata, passageiros_milhoes"
        )

    df["iata"] = df["iata"].astype(str).str.strip().str.upper()
    df["passageiros_milhoes"] = (
        df["passageiros_milhoes"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    return df


def build_passenger_analytics():
    passageiros_df = read_passengers_df()
    aeroportos_df = pd.read_csv(AIRPORTS_PATH)
    graus_df = pd.read_csv(GRAUS_PATH)
    ego_df = pd.read_csv(EGO_PATH)

    aeroportos_df["iata"] = aeroportos_df["iata"].astype(str).str.strip().str.upper()
    graus_df["aeroporto"] = graus_df["aeroporto"].astype(str).str.strip().str.upper()
    ego_df["aeroporto"] = ego_df["aeroporto"].astype(str).str.strip().str.upper()

    ranking_passageiros = passageiros_df.sort_values(
        by="passageiros_milhoes",
        ascending=False
    )

    comparativo = (
        passageiros_df
        .merge(aeroportos_df, on="iata", how="left")
        .merge(graus_df, left_on="iata", right_on="aeroporto", how="left")
        .merge(
            ego_df[["aeroporto", "densidade_ego"]],
            left_on="iata",
            right_on="aeroporto",
            how="left",
            suffixes=("", "_ego")
        )
    )

    no_grafo = comparativo.dropna(subset=["grau"]).copy()
    no_grafo["grau"] = no_grafo["grau"].astype(int)
    no_grafo["densidade_ego"] = no_grafo["densidade_ego"].fillna(0).astype(float)

    passageiros_por_regiao = (
        no_grafo
        .groupby("regiao", as_index=False)["passageiros_milhoes"]
        .sum()
        .sort_values(by="passageiros_milhoes", ascending=False)
    )

    por_conexao = no_grafo[no_grafo["grau"] > 0].copy()
    por_conexao["passageiros_por_conexao"] = (
        por_conexao["passageiros_milhoes"] / por_conexao["grau"]
    )

    aeroportos_do_grafo = set(aeroportos_df["iata"])
    aeroportos_com_passageiros = set(passageiros_df["iata"])

    fora_do_grafo = sorted(aeroportos_com_passageiros - aeroportos_do_grafo)
    sem_passageiros = sorted(aeroportos_do_grafo - aeroportos_com_passageiros)

    return {
        "ranking_passageiros": json.loads(
            ranking_passageiros.round(4).to_json(orient="records", force_ascii=False)
        ),
        "passageiros_por_regiao": json.loads(
            passageiros_por_regiao.round(4).to_json(orient="records", force_ascii=False)
        ),
        "grau_x_passageiros": json.loads(
            no_grafo[[
                "iata",
                "cidade",
                "regiao",
                "grau",
                "passageiros_milhoes",
                "densidade_ego"
            ]]
            .sort_values(by="passageiros_milhoes", ascending=False)
            .round(4)
            .to_json(orient="records", force_ascii=False)
        ),
        "passageiros_por_conexao": json.loads(
            por_conexao[[
                "iata",
                "cidade",
                "regiao",
                "grau",
                "passageiros_milhoes",
                "passageiros_por_conexao"
            ]]
            .sort_values(by="passageiros_por_conexao", ascending=False)
            .round(4)
            .to_json(orient="records", force_ascii=False)
        ),
        "aeroportos_fora_do_grafo": fora_do_grafo,
        "aeroportos_sem_passageiros": sem_passageiros
    }

def read_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def read_csv_records(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    df = pd.read_csv(path)

    # Converte para JSON e volta para dict para evitar problemas com tipos numpy.
    return json.loads(df.to_json(orient="records", force_ascii=False))


def get_graph():
    return build_airport_graph(
        str(AIRPORTS_PATH),
        str(ADJACENCIES_PATH)
    )


@app.errorhandler(FileNotFoundError)
def handle_file_not_found(error):
    return jsonify({
        "erro": "Arquivo necessário não encontrado.",
        "detalhe": str(error),
        "sugestao": "Execute: python -m src.solve e depois python -m src.api.app"
    }), 404


@app.errorhandler(ValueError)
def handle_value_error(error):
    return jsonify({
        "erro": "Erro de validação.",
        "detalhe": str(error)
    }), 400


@app.route("/", methods=["GET"])
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/grafo", methods=["GET"])
def grafo_page():
    return send_from_directory(FRONTEND_DIR, "grafo.html")


@app.route("/dashboard", methods=["GET"])
def dashboard_page():
    return send_from_directory(FRONTEND_DIR, "dashboard.html")


@app.route("/insights", methods=["GET"])
def insights_page():
    return send_from_directory(FRONTEND_DIR, "insights.html")


@app.route("/css/<path:filename>", methods=["GET"])
def serve_css(filename):
    return send_from_directory(FRONTEND_DIR / "css", filename)


@app.route("/js/<path:filename>", methods=["GET"])
def serve_js(filename):
    return send_from_directory(FRONTEND_DIR / "js", filename)

@app.route("/api/grafo", methods=["GET"])
def api_grafo():
    graph = get_graph()

    ego_df = pd.read_csv(EGO_PATH)
    ego_map = dict(zip(ego_df["aeroporto"], ego_df["densidade_ego"]))

    nodes = []

    for node in graph.nodes():
        attrs = graph.get_node_attrs(node)
        grau = graph.degree(node)
        densidade_ego = float(ego_map.get(node, 0))
        

        coord = AIRPORT_COORDS.get(node, {"lat": None, "lon": None})
        nodes.append({
            "id": node,
            "label": node,
            "cidade": attrs.get("cidade"),
            "regiao": attrs.get("regiao"),
            "grau": grau,
            "densidade_ego": densidade_ego,
            "lat": coord["lat"],
            "lon": coord["lon"],
            "group": attrs.get("regiao"),
            "title": (
                f"<b>{node}</b><br>"
                f"Cidade: {attrs.get('cidade')}<br>"
                f"Região: {attrs.get('regiao')}<br>"
                f"Grau: {grau}<br>"
                f"Densidade ego: {densidade_ego:.4f}"
            )
        })

    edges = []

    for origem, destino, attrs in graph.edges():
        peso = float(attrs.get("peso", 1.0))
        tipo = attrs.get("tipo_conexao", "")
        justificativa = attrs.get("justificativa", "")

        edges.append({
            "from": origem,
            "to": destino,
            "peso": peso,
            "label": f"{peso:.1f} km",
            "tipo_conexao": tipo,
            "justificativa": justificativa,
            "title": (
                f"{origem} → {destino}<br>"
                f"Peso: {peso:.1f} km<br>"
                f"Tipo: {tipo}<br>"
                f"Justificativa: {justificativa}"
            )
        })

    return jsonify({
        "nodes": nodes,
        "edges": edges
    })

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "mensagem": "API Flask da Parte 1 em execução."
    })


@app.route("/api/aeroportos", methods=["GET"])
def aeroportos():
    return jsonify(read_csv_records(AIRPORTS_PATH))


@app.route("/api/arestas", methods=["GET"])
def arestas():
    return jsonify(read_csv_records(ADJACENCIES_PATH))


@app.route("/api/metricas/global", methods=["GET"])
def metricas_global():
    return jsonify(read_json(GLOBAL_PATH))


@app.route("/api/metricas/regioes", methods=["GET"])
def metricas_regioes():
    return jsonify(read_json(REGIOES_PATH))


@app.route("/api/metricas/graus", methods=["GET"])
def metricas_graus():
    return jsonify(read_csv_records(GRAUS_PATH))


@app.route("/api/metricas/ego", methods=["GET"])
def metricas_ego():
    return jsonify(read_csv_records(EGO_PATH))


@app.route("/api/distancias", methods=["GET"])
def distancias():
    return jsonify(read_csv_records(DISTANCIAS_PATH))


@app.route("/api/rotas", methods=["GET"])
def calcular_rota():
    origem = request.args.get("origem", "").strip().upper()
    destino = request.args.get("destino", "").strip().upper()

    if not origem or not destino:
        return jsonify({
            "erro": "Informe origem e destino.",
            "exemplo": "/api/rotas?origem=REC&destino=POA"
        }), 400

    if origem == destino:
        return jsonify({
            "erro": "Origem e destino devem ser diferentes."
        }), 400

    graph = get_graph()

    resultado = dijkstra(graph, origem, destino)

    return jsonify({
        "origem": resultado["origem"],
        "destino": resultado["destino"],
        "custo": round(resultado["custo"], 2),
        "caminho": resultado["caminho"],
        "caminho_formatado": " -> ".join(resultado["caminho"])
    })


@app.route("/api/aeroportos/<iata>/conexoes", methods=["GET"])
def conexoes_aeroporto(iata):
    iata = iata.strip().upper()

    graph = get_graph()

    if not graph.has_node(iata):
        return jsonify({
            "erro": f"Aeroporto não encontrado: {iata}"
        }), 404

    conexoes = []

    for vizinho, attrs in graph.neighbors_with_attrs(iata):
        conexoes.append({
            "origem": iata,
            "destino": vizinho,
            "peso": attrs.get("peso"),
            "tipo_conexao": attrs.get("tipo_conexao"),
            "justificativa": attrs.get("justificativa")
        })

    return jsonify({
        "aeroporto": iata,
        "grau": graph.degree(iata),
        "conexoes": conexoes
    })


def format_decimal_br(value, decimal_places=1):
    return f"{value:.{decimal_places}f}".replace(".", ",")


def build_dashboard_insights():
    global_data = read_json(GLOBAL_PATH)
    graus_df = pd.read_csv(GRAUS_PATH)
    ego_df = pd.read_csv(EGO_PATH)
    analytics = build_passenger_analytics()

    graus_df["grau"] = graus_df["grau"].astype(int)
    ego_df["grau"] = ego_df["grau"].astype(int)
    ego_df["densidade_ego"] = ego_df["densidade_ego"].astype(float)

    hub = graus_df.sort_values(
        by=["grau", "aeroporto"],
        ascending=[False, True]
    ).iloc[0]

    ranking_passageiros = analytics["ranking_passageiros"]
    lider_passageiros = ranking_passageiros[0]
    segundo_passageiros = ranking_passageiros[1]

    regioes = analytics["passageiros_por_regiao"]
    lider_regional = regioes[0]
    total_regional = sum(item["passageiros_milhoes"] for item in regioes)
    participacao_regional = (
        lider_regional["passageiros_milhoes"] / total_regional * 100
        if total_regional else 0
    )

    comparativo_df = pd.DataFrame(analytics["grau_x_passageiros"])
    correlacao = comparativo_df["grau"].corr(
        comparativo_df["passageiros_milhoes"]
    )
    correlacao = 0.0 if pd.isna(correlacao) else float(correlacao)

    if abs(correlacao) >= 0.7:
        intensidade_correlacao = "forte"
    elif abs(correlacao) >= 0.4:
        intensidade_correlacao = "moderada"
    else:
        intensidade_correlacao = "fraca"

    lider_por_conexao = analytics["passageiros_por_conexao"][0]

    maior_densidade = float(ego_df["densidade_ego"].max())
    lideres_ego = (
        ego_df[ego_df["densidade_ego"] == maior_densidade]
        .sort_values(by=["grau", "aeroporto"], ascending=[False, True])
    )
    destaque_ego = lideres_ego.iloc[0]
    aeroportos_empatados = lideres_ego["aeroporto"].astype(str).tolist()

    conexoes_possiveis = max(int(global_data["ordem"]) - 1, 0)
    percentual_conexoes = (
        int(hub["grau"]) / conexoes_possiveis * 100
        if conexoes_possiveis else 0
    )

    return {
        "ranking_graus": {
            "aeroporto": str(hub["aeroporto"]),
            "grau": int(hub["grau"]),
            "conexoes_possiveis": conexoes_possiveis,
            "percentual_conexoes": round(percentual_conexoes, 1),
            "interpretacao": (
                f"{hub['aeroporto']} é o principal hub estrutural: conecta-se "
                f"diretamente a {int(hub['grau'])} dos {conexoes_possiveis} "
                "outros aeroportos da rede."
            )
        },
        "ranking_passageiros": {
            "aeroporto": str(lider_passageiros["iata"]),
            "passageiros_milhoes": float(lider_passageiros["passageiros_milhoes"]),
            "segundo_aeroporto": str(segundo_passageiros["iata"]),
            "segundo_passageiros_milhoes": float(
                segundo_passageiros["passageiros_milhoes"]
            ),
            "diferenca_milhoes": round(
                lider_passageiros["passageiros_milhoes"]
                - segundo_passageiros["passageiros_milhoes"],
                1
            ),
            "interpretacao": (
                f"{lider_passageiros['iata']} lidera o volume de passageiros e "
                f"supera {segundo_passageiros['iata']}, segundo colocado, por "
                f"{format_decimal_br(lider_passageiros['passageiros_milhoes'] - segundo_passageiros['passageiros_milhoes'])} "
                "milhões de passageiros."
            )
        },
        "passageiros_por_regiao": {
            "regiao": str(lider_regional["regiao"]),
            "passageiros_milhoes": float(lider_regional["passageiros_milhoes"]),
            "participacao_percentual": round(participacao_regional, 1),
            "aeroportos_considerados": len(analytics["grau_x_passageiros"]),
            "aeroportos_fora_do_grafo": analytics["aeroportos_fora_do_grafo"],
            "interpretacao": (
                f"A região {lider_regional['regiao']} concentra "
                f"{format_decimal_br(participacao_regional)}% do tráfego dos aeroportos que "
                "possuem dados de passageiros e pertencem ao grafo."
            )
        },
        "grau_x_passageiros": {
            "correlacao": round(correlacao, 4),
            "intensidade": intensidade_correlacao,
            "aeroporto_maior_grau": str(hub["aeroporto"]),
            "aeroporto_maior_trafego": str(lider_passageiros["iata"]),
            "interpretacao": (
                f"A correlação é positiva e {intensidade_correlacao}: aeroportos "
                "mais conectados tendem a movimentar mais passageiros, mas o grau "
                "não explica sozinho o volume de tráfego."
            )
        },
        "passageiros_por_conexao": {
            "aeroporto": str(lider_por_conexao["iata"]),
            "passageiros_por_conexao": float(
                lider_por_conexao["passageiros_por_conexao"]
            ),
            "passageiros_milhoes": float(
                lider_por_conexao["passageiros_milhoes"]
            ),
            "grau": int(lider_por_conexao["grau"]),
            "interpretacao": (
                f"{lider_por_conexao['iata']} apresenta a maior razão de passageiros "
                "por conexão direta, combinando tráfego elevado com poucas conexões "
                "na rede modelada."
            )
        },
        "densidade_ego": {
            "aeroporto_destaque": str(destaque_ego["aeroporto"]),
            "densidade_ego": maior_densidade,
            "grau_destaque": int(destaque_ego["grau"]),
            "aeroportos_empatados": aeroportos_empatados,
            "interpretacao": (
                f"{len(aeroportos_empatados)} aeroportos atingem densidade ego "
                f"{format_decimal_br(maior_densidade)}. Entre eles, {destaque_ego['aeroporto']} "
                "tem o maior grau, reunindo uma vizinhança totalmente conectada e "
                "mais ampla que a dos demais empatados."
            )
        }
    }


@app.route("/api/insights", methods=["GET"])
def insights():
    return jsonify(build_dashboard_insights())

@app.route("/api/passageiros", methods=["GET"])
def passageiros():
    return jsonify(read_csv_records(PASSENGERS_PATH))


@app.route("/api/analytics/passageiros", methods=["GET"])
def analytics_passageiros():
    return jsonify(build_passenger_analytics())

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
