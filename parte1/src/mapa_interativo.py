from pathlib import Path
import json

import pandas as pd
import plotly.graph_objects as go

from src.graphs.io import build_airport_graph


DATA_DIR = Path("data")
OUT_DIR = Path("out")

AIRPORTS_PATH = DATA_DIR / "aeroportos_data.csv"
ADJACENCIES_PATH = DATA_DIR / "adjacencias_aeroportos.csv"
EGO_PATH = OUT_DIR / "ego_aeroportos.csv"

OUTPUT_HTML = OUT_DIR / "grafo_interativo.html"


# Coordenadas aproximadas dos aeroportos/cidades usadas no projeto.
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


REGION_COLORS = {
    "Norte": "#2ca02c",
    "Nordeste": "#ff7f0e",
    "Centro-Oeste": "#9467bd",
    "Sudeste": "#1f77b4",
    "Sul": "#d62728",
}

IATA_TEXT_POSITIONS = {
    "REC": "middle right",
    "JPA": "middle right",
    "NAT": "top right",
}

def ensure_out_dir() -> None:
    OUT_DIR.mkdir(exist_ok=True)


def load_ego_density() -> dict:
    """
    Lê out/ego_aeroportos.csv e retorna:
    {
        "REC": 0.45,
        "GRU": 0.38
    }
    """

    if not EGO_PATH.exists():
        raise FileNotFoundError(
            "Arquivo out/ego_aeroportos.csv não encontrado. "
            "Execute primeiro: python -m src.solve"
        )

    df = pd.read_csv(EGO_PATH)

    if "aeroporto" not in df.columns or "densidade_ego" not in df.columns:
        raise ValueError(
            "O arquivo ego_aeroportos.csv precisa conter as colunas "
            "'aeroporto' e 'densidade_ego'."
        )

    return dict(zip(df["aeroporto"], df["densidade_ego"]))


def build_all_edges_trace(graph):
    """
    Cria a camada fixa de conexões do grafo.
    """

    edge_lons = []
    edge_lats = []
    edge_texts = []

    for origem, destino, attrs in graph.edges():
        if origem not in AIRPORT_COORDS or destino not in AIRPORT_COORDS:
            continue

        origem_coord = AIRPORT_COORDS[origem]
        destino_coord = AIRPORT_COORDS[destino]

        peso = attrs.get("peso", "")
        tipo = attrs.get("tipo_conexao", "")
        justificativa = attrs.get("justificativa", "")

        hover = (
            f"{origem} → {destino}<br>"
            f"Tipo: {tipo}<br>"
            f"Peso/distância: {peso} km<br>"
            f"Justificativa: {justificativa}"
        )

        edge_lons.extend([origem_coord["lon"], destino_coord["lon"], None])
        edge_lats.extend([origem_coord["lat"], destino_coord["lat"], None])
        edge_texts.extend([hover, hover, None])

    return go.Scattergeo(
        lon=edge_lons,
        lat=edge_lats,
        mode="lines",
        line=dict(width=1, color="rgba(110,110,110,0.45)"),
        hoverinfo="text",
        text=edge_texts,
        name="Conexões fixas do grafo"
    )


def build_airports_trace(graph, ego_density: dict):
    """
    Cria a camada fixa de aeroportos.
    """

    lons = []
    lats = []
    labels = []
    colors = []
    sizes = []
    hover_texts = []
    text_positions = []

    for airport in graph.nodes():
        if airport not in AIRPORT_COORDS:
            continue

        attrs = graph.get_node_attrs(airport)
        cidade = attrs.get("cidade", "")
        regiao = attrs.get("regiao", "")
        grau = graph.degree(airport)
        densidade = float(ego_density.get(airport, 0))

        coord = AIRPORT_COORDS[airport]

        lons.append(coord["lon"])
        lats.append(coord["lat"])
        labels.append(airport)
        colors.append(REGION_COLORS.get(regiao, "#7f7f7f"))
        sizes.append(10 + grau)
        text_positions.append(
            IATA_TEXT_POSITIONS.get(airport, "top center")
            )

        hover_texts.append(
            f"<b>{airport}</b><br>"
            f"Cidade: {cidade}<br>"
            f"Região: {regiao}<br>"
            f"Grau: {grau}<br>"
            f"Densidade ego: {densidade:.4f}"
        )

    return go.Scattergeo(
        lon=lons,
        lat=lats,
        text=labels,
        mode="markers+text",
        textposition=text_positions,
        marker=dict(
            size=sizes,
            color=colors,
            line=dict(width=1, color="black"),
            opacity=0.92
        ),
        hovertext=hover_texts,
        hoverinfo="text",
        name="Aeroportos fixos"
    )


def build_empty_route_trace():
    """
    Camada inicialmente vazia.
    O JavaScript preencherá essa camada quando o usuário escolher uma rota.
    """

    return go.Scattergeo(
        lon=[],
        lat=[],
        mode="lines+markers",
        line=dict(width=5, color="#e11d48"),
        marker=dict(size=10, color="#e11d48"),
        hoverinfo="text",
        text=[],
        name="Rota escolhida"
    )

def build_empty_selected_connections_trace():
    """
    Camada inicialmente vazia.
    O JavaScript preencherá essa camada quando o usuário clicar em um aeroporto,
    destacando todas as arestas/conexões diretas desse aeroporto.
    """

    return go.Scattergeo(
        lon=[],
        lat=[],
        mode="lines",
        line=dict(width=4, color="#facc15"),
        hoverinfo="text",
        text=[],
        name="Conexões do aeroporto selecionado"
    )

def build_empty_search_trace():
    """
    Camada vazia usada para destacar aeroporto pesquisado.
    """

    return go.Scattergeo(
        lon=[],
        lat=[],
        mode="markers+text",
        text=[],
        textposition="bottom center",
        marker=dict(
            size=24,
            color="yellow",
            line=dict(width=3, color="black")
        ),
        hoverinfo="text",
        hovertext=[],
        name="Aeroporto buscado"
    )


def build_graph_data_for_js(graph) -> tuple[dict, dict, list]:
    """
    Prepara os dados do grafo para uso no JavaScript.

    Retorna:
    - adjacency: lista de adjacência com pesos;
    - edges_info: informações textuais das arestas;
    - edges_list: lista simples de arestas.
    """

    adjacency = {}
    edges_info = {}
    edges_list = []

    for node in graph.nodes():
        adjacency[node] = []

    for origem, destino, attrs in graph.edges():
        peso = float(attrs.get("peso", 1.0))
        tipo = attrs.get("tipo_conexao", "")
        justificativa = attrs.get("justificativa", "")

        adjacency[origem].append({
            "destino": destino,
            "peso": peso
        })

        adjacency[destino].append({
            "destino": origem,
            "peso": peso
        })

        edge_key = "|".join(sorted([origem, destino]))

        edges_info[edge_key] = {
            "origem": origem,
            "destino": destino,
            "peso": peso,
            "tipo_conexao": tipo,
            "justificativa": justificativa
        }

        edges_list.append({
            "origem": origem,
            "destino": destino,
            "peso": peso,
            "tipo_conexao": tipo,
            "justificativa": justificativa
        })

    return adjacency, edges_info, edges_list


def create_map_html() -> None:
    ensure_out_dir()

    graph = build_airport_graph(
        str(AIRPORTS_PATH),
        str(ADJACENCIES_PATH)
    )

    ego_density = load_ego_density()

    fig = go.Figure()

    # Camada 0: conexões fixas
    fig.add_trace(build_all_edges_trace(graph))

    # Camada 1: rota escolhida dinamicamente
    route_trace_index = len(fig.data)
    fig.add_trace(build_empty_route_trace())

    # Camada 2: conexões do aeroporto selecionado por clique
    selected_connections_trace_index = len(fig.data)
    fig.add_trace(build_empty_selected_connections_trace())

    # Camada 3: aeroportos fixos
    airport_trace_index = len(fig.data)
    fig.add_trace(build_airports_trace(graph, ego_density))

    # Camada 4: aeroporto buscado
    search_trace_index = len(fig.data)
    fig.add_trace(build_empty_search_trace())

    fig.update_layout(
        title=dict(
            text="Grafo Interativo de Aeroportos no Mapa do Brasil",
            x=0.5,
            xanchor="center"
        ),
        showlegend=True,
        height=760,
        margin=dict(l=0, r=0, t=60, b=0),
        geo=dict(
            scope="south america",
            projection_type="mercator",
            showland=True,
            landcolor="rgb(242, 242, 242)",
            showocean=True,
            oceancolor="rgb(221, 235, 247)",
            showcountries=True,
            countrycolor="rgb(120, 120, 120)",
            showsubunits=True,
            subunitcolor="rgb(190, 190, 190)",
            lataxis=dict(range=[-35, 7]),
            lonaxis=dict(range=[-75, -32]),
            center=dict(lat=-14.2, lon=-51.9),
            resolution=50
        ),
        legend=dict(
            title="Camadas",
            orientation="v",
            x=0.01,
            y=0.99
        )
    )

    plot_html = fig.to_html(
        include_plotlyjs=True,
        full_html=False,
        div_id="grafo-brasil"
    )

    coords_for_js = {
        code: {
            "lat": data["lat"],
            "lon": data["lon"]
        }
        for code, data in AIRPORT_COORDS.items()
    }

    airport_info_for_js = {}

    for airport in graph.nodes():
        attrs = graph.get_node_attrs(airport)

        airport_info_for_js[airport] = {
            "cidade": attrs.get("cidade", ""),
            "regiao": attrs.get("regiao", ""),
            "grau": graph.degree(airport),
            "densidade_ego": float(ego_density.get(airport, 0))
        }

    adjacency, edges_info, edges_list = build_graph_data_for_js(graph)

    airport_codes = sorted(graph.nodes())

    options_html = "\n".join(
        f'<option value="{code}">{code}</option>'
        for code in airport_codes
    )

    html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <title>Grafo Interativo de Aeroportos</title>

    <style>
        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f7f7f7;
        }}

        .topbar {{
            padding: 14px 18px;
            background: #111827;
            color: white;
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .topbar h1 {{
            font-size: 18px;
            margin: 0 18px 0 0;
            font-weight: 700;
        }}

        .topbar label {{
            font-size: 13px;
            color: #e5e7eb;
        }}

        .topbar select,
        .topbar input {{
            padding: 8px 10px;
            border-radius: 6px;
            border: none;
            font-size: 14px;
            text-transform: uppercase;
        }}

        .topbar button {{
            padding: 8px 12px;
            border-radius: 6px;
            border: none;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            background: #f3f4f6;
            color: #111827;
        }}

        .topbar button:hover {{
            opacity: 0.9;
        }}

        .info {{
            padding: 10px 18px;
            background: white;
            border-bottom: 1px solid #ddd;
            font-size: 14px;
            line-height: 1.45;
        }}

        .info strong {{
            color: #111827;
        }}

        .badge {{
            display: inline-block;
            padding: 2px 6px;
            border-radius: 4px;
            background: #e5e7eb;
            margin-right: 4px;
            font-size: 12px;
        }}

        #grafo-brasil {{
            width: 100%;
            height: calc(100vh - 132px);
        }}
    </style>
</head>

<body>
    <div class="topbar">
        <h1>Grafo de Aeroportos — Brasil</h1>

        <label for="origemSelect">Origem:</label>
        <select id="origemSelect">
            {options_html}
        </select>

        <label for="destinoSelect">Destino:</label>
        <select id="destinoSelect">
            {options_html}
        </select>

        <button onclick="calculateSelectedRoute()">Calcular rota</button>
        <button onclick="resetRoute()">Limpar rota</button>

        <input
            id="airportSearch"
            type="text"
            placeholder="Buscar IATA"
            maxlength="3"
        />
        <button onclick="searchAirport()">Buscar</button>
        <button onclick="clearSelectedConnections()">Limpar conexões</button>
        <button onclick="resetMap()">Resetar mapa</button>
    </div>

    <div class="info" id="routeInfo">
        <strong>Mapa interativo:</strong>
        os aeroportos e conexões permanecem fixos; escolha origem e destino para destacar dinamicamente o menor caminho pelo algoritmo de Dijkstra.
    </div>

    {plot_html}

    <script>
        const coords = {json.dumps(coords_for_js, ensure_ascii=False)};
        const airportInfo = {json.dumps(airport_info_for_js, ensure_ascii=False)};
        const adjacency = {json.dumps(adjacency, ensure_ascii=False)};
        const edgesInfo = {json.dumps(edges_info, ensure_ascii=False)};
        const routeTraceIndex = {route_trace_index};
        const selectedConnectionsTraceIndex = {selected_connections_trace_index};
        const airportTraceIndex = {airport_trace_index};
        const searchTraceIndex = {search_trace_index};


        function edgeKey(a, b) {{
            return [a, b].sort().join("|");
        }}
        function showAirportConnections(code) {{
            if (!adjacency[code] || !coords[code]) {{
                return;
                }}
            const lons = [];
            const lats = [];
            const texts = [];
            const connections = adjacency[code];

            for (const edge of connections) {{
                const destino = edge.destino;
                
                if (!coords[destino]) {{
                      continue;
                      }}

                const c1 = coords[code];
                const c2 = coords[destino];

                const key = edgeKey(code, destino);
                const edgeInfo = edgesInfo[key];

                let hover =
                    code + " → " + destino + "<br>" +
                    "Peso/distância: " + edge.peso.toFixed(2) + " km";

                if (edgeInfo) {{
                    hover =
                        code + " → " + destino + "<br>" +
                        "Peso/distância: " + edgeInfo.peso.toFixed(2) + " km<br>" +
                        "Tipo: " + edgeInfo.tipo_conexao + "<br>" +
                        "Justificativa: " + edgeInfo.justificativa;
                        }}

                lons.push(c1.lon, c2.lon, null);
                lats.push(c1.lat, c2.lat, null);
                texts.push(hover, hover, null);
                }}
            Plotly.restyle(
                "grafo-brasil",
                {{
                    lon: [lons],
                    lat: [lats],
                    text: [texts],
                    name: ["Conexões de " + code]
                    }},
                [selectedConnectionsTraceIndex]
            );

            const info = airportInfo[code];

            const connectionBadges = connections
                .map(edge =>
                    '<span class="badge">' +
                    code + " → " + edge.destino +
                    " (" + edge.peso.toFixed(1) + " km)" +
                    '</span>'
                )
                .join(" ");

            document.getElementById("routeInfo").innerHTML =
                "<strong>Aeroporto selecionado:</strong> " + code +
                " | Cidade: " + info.cidade +
                " | Região: " + info.regiao +
                " | Grau: " + info.grau +
                " | Densidade ego: " + info.densidade_ego.toFixed(4) +
                "<br><strong>Conexões diretas:</strong> " + connectionBadges;
                }}

        function dijkstra(start, end) {{
            const distances = {{}};
            const previous = {{}};
            const visited = new Set();
            const nodes = Object.keys(adjacency);

            for (const node of nodes) {{
                distances[node] = Infinity;
                previous[node] = null;
            }}

            distances[start] = 0;

            while (visited.size < nodes.length) {{
                let current = null;
                let currentDistance = Infinity;

                for (const node of nodes) {{
                    if (!visited.has(node) && distances[node] < currentDistance) {{
                        current = node;
                        currentDistance = distances[node];
                    }}
                }}

                if (current === null) {{
                    break;
                }}

                if (current === end) {{
                    break;
                }}

                visited.add(current);

                for (const edge of adjacency[current]) {{
                    const neighbor = edge.destino;
                    const weight = edge.peso;
                    const newDistance = distances[current] + weight;

                    if (newDistance < distances[neighbor]) {{
                        distances[neighbor] = newDistance;
                        previous[neighbor] = current;
                    }}
                }}
            }}

            const path = [];
            let current = end;

            while (current !== null) {{
                path.push(current);

                if (current === start) {{
                    break;
                }}

                current = previous[current];
            }}

            path.reverse();

            if (path.length === 0 || path[0] !== start) {{
                return {{
                    custo: Infinity,
                    caminho: []
                }};
            }}

            return {{
                custo: distances[end],
                caminho: path
            }};
        }}

        function pathToCoordinates(path) {{
            const lons = [];
            const lats = [];
            const texts = [];

            for (let i = 0; i < path.length - 1; i++) {{
                const origem = path[i];
                const destino = path[i + 1];

                const c1 = coords[origem];
                const c2 = coords[destino];

                const key = edgeKey(origem, destino);
                const edge = edgesInfo[key];

                let hover = origem + " → " + destino;

                if (edge) {{
                    hover =
                        origem + " → " + destino + "<br>" +
                        "Peso/distância: " + edge.peso.toFixed(2) + " km<br>" +
                        "Tipo: " + edge.tipo_conexao + "<br>" +
                        "Justificativa: " + edge.justificativa;
                }}

                lons.push(c1.lon, c2.lon, null);
                lats.push(c1.lat, c2.lat, null);
                texts.push(hover, hover, null);
            }}

            return {{
                lons: lons,
                lats: lats,
                texts: texts
            }};
        }}

        function updateRoute(start, end) {{
            if (start === end) {{
                alert("Origem e destino devem ser diferentes.");
                return;
            }}

            const result = dijkstra(start, end);

            if (!result.caminho || result.caminho.length === 0 || !isFinite(result.custo)) {{
                alert("Não foi possível encontrar caminho entre os aeroportos selecionados.");
                return;
            }}

            const routeCoords = pathToCoordinates(result.caminho);

            Plotly.restyle(
                "grafo-brasil",
                {{
                    lon: [routeCoords.lons],
                    lat: [routeCoords.lats],
                    text: [routeCoords.texts],
                    name: ["Rota escolhida: " + start + " → " + end]
                }},
                [routeTraceIndex]
            );

            let minLon = Infinity;
            let maxLon = -Infinity;
            let minLat = Infinity;
            let maxLat = -Infinity;

            for (const airport of result.caminho) {{
                minLon = Math.min(minLon, coords[airport].lon);
                maxLon = Math.max(maxLon, coords[airport].lon);
                minLat = Math.min(minLat, coords[airport].lat);
                maxLat = Math.max(maxLat, coords[airport].lat);
            }}

            const lonPadding = 5;
            const latPadding = 5;

            Plotly.relayout(
                "grafo-brasil",
                {{
                    "geo.lonaxis.range": [minLon - lonPadding, maxLon + lonPadding],
                    "geo.lataxis.range": [minLat - latPadding, maxLat + latPadding],
                    "geo.center.lon": (minLon + maxLon) / 2,
                    "geo.center.lat": (minLat + maxLat) / 2
                }}
            );

            const routeBadges = result.caminho
                .map(code => '<span class="badge">' + code + '</span>')
                .join("");

            document.getElementById("routeInfo").innerHTML =
                "<strong>Rota calculada:</strong> " + start + " → " + end +
                " | <strong>Custo total:</strong> " + result.custo.toFixed(2) + " km<br>" +
                "<strong>Caminho:</strong> " + routeBadges;
        }}

        function calculateSelectedRoute() {{
            const start = document.getElementById("origemSelect").value;
            const end = document.getElementById("destinoSelect").value;
            updateRoute(start, end);
        }}

        function setRoute(start, end) {{
            document.getElementById("origemSelect").value = start;
            document.getElementById("destinoSelect").value = end;
            updateRoute(start, end);
        }}

        function resetRoute() {{
            Plotly.restyle(
                "grafo-brasil",
                {{
                    lon: [[]],
                    lat: [[]],
                    text: [[]],
                    name: ["Rota escolhida"]
                }},
                [routeTraceIndex]
            );

            document.getElementById("routeInfo").innerHTML =
                "<strong>Mapa interativo:</strong> os aeroportos e conexões permanecem fixos; escolha origem e destino para destacar dinamicamente o menor caminho pelo algoritmo de Dijkstra.";
        }}

        function searchAirport() {{
            const input = document.getElementById("airportSearch");
            const code = input.value.trim().toUpperCase();

            if (!code || !coords[code]) {{
                alert("Aeroporto não encontrado. Use um código IATA existente, como REC, GRU, BSB, MAO ou POA.");
                return;
            }}

            const point = coords[code];
            const info = airportInfo[code];

            const hover =
                "<b>" + code + "</b><br>" +
                "Cidade: " + info.cidade + "<br>" +
                "Região: " + info.regiao + "<br>" +
                "Grau: " + info.grau + "<br>" +
                "Densidade ego: " + info.densidade_ego.toFixed(4);

            Plotly.restyle(
                "grafo-brasil",
                {{
                    lon: [[point.lon]],
                    lat: [[point.lat]],
                    text: [[code]],
                    hovertext: [[hover]]
                }},
                [searchTraceIndex]
            );

            Plotly.relayout(
                "grafo-brasil",
                {{
                    "geo.center.lon": point.lon,
                    "geo.center.lat": point.lat,
                    "geo.lonaxis.range": [point.lon - 8, point.lon + 8],
                    "geo.lataxis.range": [point.lat - 8, point.lat + 8]
                }}
            );

            document.getElementById("routeInfo").innerHTML =
                "<strong>Aeroporto buscado:</strong> " + code +
                " | Cidade: " + info.cidade +
                " | Região: " + info.regiao +
                " | Grau: " + info.grau +
                " | Densidade ego: " + info.densidade_ego.toFixed(4);
        }}

        function resetMap() {{
            Plotly.restyle(
                "grafo-brasil",
                {{
                    lon: [[]],
                    lat: [[]],
                    text: [[]],
                    hovertext: [[]]
                }},
                [searchTraceIndex]
            );
            Plotly.restyle(
                "grafo-brasil",
                {{
                    lon: [[]],
                    lat: [[]],
                    text: [[]],
                    name: ["Conexões do aeroporto selecionado"]
                }},
                [selectedConnectionsTraceIndex]
            );
            Plotly.restyle(
                "grafo-brasil",
                {{
                    lon: [[]],
                    lat: [[]],
                    text: [[]],
                    name: ["Rota escolhida"]
                }},
                [routeTraceIndex]
            );

            Plotly.relayout(
                "grafo-brasil",
                {{
                    "geo.center.lon": -51.9,
                    "geo.center.lat": -14.2,
                    "geo.lonaxis.range": [-75, -32],
                    "geo.lataxis.range": [-35, 7]
                }}
            );

            document.getElementById("routeInfo").innerHTML =
                "<strong>Mapa interativo:</strong> os aeroportos e conexões permanecem fixos; escolha origem e destino para destacar dinamicamente o menor caminho pelo algoritmo de Dijkstra.";
        }}
        document.getElementById("grafo-brasil").on("plotly_click", function(event) {{
            if (!event || !event.points || event.points.length === 0) {{
                return;
            }}
            const point = event.points[0];
            /*
            Só reage ao clique na camada dos aeroportos.
            Isso evita que o clique em uma linha de conexão dispare o evento indevidamente.
            */
            if (point.curveNumber !== airportTraceIndex) {{
             return;
            }}

            const code = point.text;

            if (!code || !airportInfo[code]) {{
                return;
            }}

            showAirportConnections(code);
        }});
        function clearSelectedConnections() {{
            Plotly.restyle(
                "grafo-brasil",
                {{
                    lon: [[]],
                    lat: [[]],
                    text: [[]],
                    name: ["Conexões do aeroporto selecionado"]
                }},
                [selectedConnectionsTraceIndex]
            );

            document.getElementById("routeInfo").innerHTML =
                "<strong>Mapa interativo:</strong> os aeroportos e conexões permanecem fixos; escolha origem e destino para destacar dinamicamente o menor caminho pelo algoritmo de Dijkstra.";
        }}

    </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as file:
        file.write(html)

    print(f"Arquivo gerado: {OUTPUT_HTML}")


def main() -> None:
    create_map_html()


if __name__ == "__main__":
    main()