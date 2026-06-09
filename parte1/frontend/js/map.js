let graphDataCache = null;
let selectedRoute = null;
let selectedConnections = null;
let selectedRegion = "TODAS";
let showBaseEdges = true;
let currentFocus = "BRASIL";

const regionColors = {
    "Norte": "#22c55e",
    "Nordeste": "#f97316",
    "Centro-Oeste": "#a855f7",
    "Sudeste": "#3b82f6",
    "Sul": "#ef4444"
};

const mapViews = {
    "BRASIL": {
        lon: [-75, -32],
        lat: [-35, 7],
        center: { lat: -14.2, lon: -51.9 }
    },
    "NORDESTE": {
        lon: [-46, -33],
        lat: [-18, 1],
        center: { lat: -8.8, lon: -39.5 }
    },
    "NORTE": {
        lon: [-74, -45],
        lat: [-13, 7],
        center: { lat: -3.8, lon: -58.5 }
    },
    "SUDESTE": {
        lon: [-52, -38],
        lat: [-26, -14],
        center: { lat: -21.5, lon: -44.5 }
    },
    "SUL": {
        lon: [-58, -47],
        lat: [-34, -22],
        center: { lat: -28.0, lon: -51.0 }
    },
    "CENTRO-OESTE": {
        lon: [-62, -44],
        lat: [-23, -8],
        center: { lat: -16.0, lon: -53.0 }
    }
};

const regionToFocus = {
    "TODAS": "BRASIL",
    "Norte": "NORTE",
    "Nordeste": "NORDESTE",
    "Centro-Oeste": "CENTRO-OESTE",
    "Sudeste": "SUDESTE",
    "Sul": "SUL"
};

async function initMap() {
    graphDataCache = await getGraphData();

    populateRouteSelects(graphDataCache.nodes);
    renderMap();

    const mapDiv = document.getElementById("map");

    mapDiv.on("plotly_click", async function (event) {
        if (!event || !event.points || event.points.length === 0) {
            return;
        }

        const point = event.points[0];

        if (!point.customdata) {
            return;
        }

        await highlightAirportConnections(point.customdata);
    });
}

function getAirportById(iata) {
    return graphDataCache.nodes.find(node => node.id === iata);
}

function isNodeVisible(node) {
    return selectedRegion === "TODAS" || node.regiao === selectedRegion;
}

function isEdgeVisible(origem, destino) {
    if (selectedRegion === "TODAS") {
        return true;
    }

    return origem.regiao === selectedRegion && destino.regiao === selectedRegion;
}

function getCurrentView() {
    return mapViews[currentFocus] || mapViews.BRASIL;
}

function getFocusLabel() {
    const labels = {
        "BRASIL": "Brasil inteiro",
        "NORDESTE": "Nordeste",
        "NORTE": "Norte",
        "SUDESTE": "Sudeste",
        "SUL": "Sul",
        "CENTRO-OESTE": "Centro-Oeste"
    };

    return labels[currentFocus] || "Brasil inteiro";
}

function updateMapStatus() {
    const status = document.getElementById("map-status");

    if (!status) {
        return;
    }

    const layerText = showBaseEdges ? "conexões visíveis" : "conexões ocultas";
    const regionText = selectedRegion === "TODAS" ? "todas as regiões" : selectedRegion;

    status.innerHTML = `
        <span class="status-dot"></span>
        ${getFocusLabel()} • ${regionText} • ${layerText}
    `;
}

function checksum(value) {
    return value
        .split("")
        .reduce((total, char) => total + char.charCodeAt(0), 0);
}

function makeCurvedSegment(origem, destino, steps = 18, intensity = 0.06) {
    const dx = destino.lon - origem.lon;
    const dy = destino.lat - origem.lat;
    const distance = Math.sqrt(dx * dx + dy * dy) || 1;
    const sign = checksum(`${origem.id}-${destino.id}`) % 2 === 0 ? 1 : -1;
    const offset = Math.min(2.1, Math.max(0.18, distance * intensity)) * sign;
    const px = -dy / distance;
    const py = dx / distance;
    const points = [];

    for (let step = 0; step <= steps; step++) {
        const t = step / steps;
        const bend = Math.sin(Math.PI * t) * offset;

        points.push({
            lon: origem.lon + dx * t + px * bend,
            lat: origem.lat + dy * t + py * bend * 0.72
        });
    }

    return points;
}

function pushCurvedLine(lons, lats, origem, destino, steps = 18, intensity = 0.06) {
    const points = makeCurvedSegment(origem, destino, steps, intensity);

    for (const point of points) {
        lons.push(point.lon);
        lats.push(point.lat);
    }

    lons.push(null);
    lats.push(null);
}

function emptyLineTrace(name, color, width = 1, showlegend = false) {
    return {
        type: "scattergeo",
        mode: "lines",
        lon: [],
        lat: [],
        name: name,
        showlegend: showlegend,
        line: {
            width: width,
            color: color
        },
        hoverinfo: "skip"
    };
}

function buildBaseEdgesTrace() {
    if (!showBaseEdges) {
        return emptyLineTrace("Conexões fixas", "rgba(100, 116, 139, 0.2)");
    }

    const lons = [];
    const lats = [];
    for (const edge of graphDataCache.edges) {
        const origem = getAirportById(edge.from);
        const destino = getAirportById(edge.to);

        if (!origem || !destino || origem.lat === null || destino.lat === null) {
            continue;
        }

        if (!isEdgeVisible(origem, destino)) {
            continue;
        }

        pushCurvedLine(lons, lats, origem, destino, 18, 0.045);
    }

    return {
        type: "scattergeo",
        mode: "lines",
        lon: lons,
        lat: lats,
        hoverinfo: "skip",
        name: "Conexões fixas",
        line: {
            width: 0.9,
            color: "rgba(71, 85, 105, 0.36)"
        }
    };
}

function buildAirportsTrace() {
    const lons = [];
    const lats = [];
    const labels = [];
    const customdata = [];
    const colors = [];
    const sizes = [];
    const textPositions = [];

    const labelPositions = {
        "REC": "bottom left",
        "JPA": "middle right",
        "NAT": "top right",
        "GRU": "bottom right",
        "CGH": "top left",
        "GIG": "bottom left",
        "CNF": "middle right",
        "BSB": "bottom center"
    };

    for (const node of graphDataCache.nodes) {
        if (node.lat === null || node.lon === null || !isNodeVisible(node)) {
            continue;
        }

        lons.push(node.lon);
        lats.push(node.lat);
        labels.push(node.label);
        customdata.push(node.id);
        colors.push(regionColors[node.regiao] || "#94a3b8");
        sizes.push(Math.min(30, 10 + Number(node.grau) * 1.25));
        textPositions.push(labelPositions[node.id] || "top center");

    }

    return {
        type: "scattergeo",
        mode: "markers+text",
        lon: lons,
        lat: lats,
        text: labels,
        customdata: customdata,
        textposition: textPositions,
        hoverinfo: "none",
        name: "Aeroportos",
        marker: {
            size: sizes,
            color: colors,
            opacity: 0.95,
            line: {
                width: 1.6,
                color: "#0f172a"
            }
        },
        textfont: {
            size: 12,
            color: "#0f172a",
            family: "Arial Black, Arial, sans-serif"
        }
    };
}

function buildSelectedAirportTrace() {
    if (!selectedConnections || !selectedConnections.aeroporto) {
        return {
            type: "scattergeo",
            mode: "markers",
            lon: [],
            lat: [],
            name: "Aeroporto selecionado",
            showlegend: false
        };
    }

    const airport = getAirportById(selectedConnections.aeroporto);

    if (!airport || !isNodeVisible(airport)) {
        return emptyLineTrace("Aeroporto selecionado", "#facc15");
    }

    return {
        type: "scattergeo",
        mode: "markers",
        lon: [airport.lon],
        lat: [airport.lat],
        hoverinfo: "skip",
        name: `Selecionado: ${airport.id}`,
        marker: {
            size: 36,
            color: "rgba(250, 204, 21, 0.22)",
            line: {
                width: 4,
                color: "#facc15"
            }
        }
    };
}

function buildRouteTrace() {
    if (!selectedRoute || !selectedRoute.caminho || selectedRoute.caminho.length === 0) {
        return emptyLineTrace("Rota escolhida", "#e11d48", 5, false);
    }

    const lons = [];
    const lats = [];
    for (let index = 0; index < selectedRoute.caminho.length - 1; index++) {
        const origem = getAirportById(selectedRoute.caminho[index]);
        const destino = getAirportById(selectedRoute.caminho[index + 1]);

        if (!origem || !destino) {
            continue;
        }

        pushCurvedLine(lons, lats, origem, destino, 24, 0.065);
    }

    return {
        type: "scattergeo",
        mode: "lines",
        lon: lons,
        lat: lats,
        hoverinfo: "skip",
        name: `Rota ${selectedRoute.origem} → ${selectedRoute.destino}`,
        line: {
            width: 5,
            color: "#e11d48"
        }
    };
}

function buildSelectedConnectionsTrace() {
    if (!selectedConnections || !selectedConnections.conexoes) {
        return emptyLineTrace("Conexões do aeroporto", "#facc15", 4, false);
    }

    const origem = getAirportById(selectedConnections.aeroporto);

    if (!origem || !isNodeVisible(origem)) {
        return emptyLineTrace("Conexões do aeroporto", "#facc15", 4, false);
    }

    const lons = [];
    const lats = [];
    for (const conexao of selectedConnections.conexoes) {
        const destino = getAirportById(conexao.destino);

        if (!destino || !isNodeVisible(destino)) {
            continue;
        }

        pushCurvedLine(lons, lats, origem, destino, 20, 0.055);
    }

    return {
        type: "scattergeo",
        mode: "lines",
        lon: lons,
        lat: lats,
        hoverinfo: "skip",
        name: `Conexões de ${selectedConnections.aeroporto}`,
        line: {
            width: 4,
            color: "#facc15"
        }
    };
}

function renderMap() {
    const view = getCurrentView();
    const traces = [
        buildBaseEdgesTrace(),
        buildSelectedConnectionsTrace(),
        buildRouteTrace(),
        buildAirportsTrace(),
        buildSelectedAirportTrace()
    ];

    const layout = {
        paper_bgcolor: "#f8fafc",
        plot_bgcolor: "#f8fafc",
        showlegend: true,
        margin: {
            l: 0,
            r: 0,
            t: 0,
            b: 0
        },
        geo: {
            scope: "south america",
            projection: {
                type: "mercator"
            },
            showland: true,
            landcolor: "rgb(241, 245, 249)",
            showocean: true,
            oceancolor: "rgb(219, 234, 254)",
            showcountries: true,
            countrycolor: "rgb(100, 116, 139)",
            showsubunits: true,
            subunitcolor: "rgb(203, 213, 225)",
            lataxis: {
                range: view.lat
            },
            lonaxis: {
                range: view.lon
            },
            center: view.center,
            resolution: 50
        },
        legend: {
            orientation: "h",
            x: 0.02,
            y: 0.02,
            bgcolor: "rgba(255,255,255,0.9)",
            bordercolor: "rgba(100,116,139,0.35)",
            borderwidth: 1,
            font: {
                color: "#0f172a",
                size: 11
            }
        }
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: [
            "select2d",
            "lasso2d"
        ]
    };

    Plotly.react("map", traces, layout, config);
    updateMapStatus();
}

function populateRouteSelects(nodes) {
    const originSelect = document.getElementById("route-origin");
    const destinationSelect = document.getElementById("route-destination");

    originSelect.innerHTML = "";
    destinationSelect.innerHTML = "";

    const sortedNodes = [...nodes].sort((a, b) => a.id.localeCompare(b.id));

    for (const node of sortedNodes) {
        const optionOrigin = document.createElement("option");
        optionOrigin.value = node.id;
        optionOrigin.textContent = `${node.id} — ${node.cidade}`;

        const optionDestination = document.createElement("option");
        optionDestination.value = node.id;
        optionDestination.textContent = `${node.id} — ${node.cidade}`;

        originSelect.appendChild(optionOrigin);
        destinationSelect.appendChild(optionDestination);
    }

    if (nodes.some(node => node.id === "REC")) {
        originSelect.value = "REC";
    }

    if (nodes.some(node => node.id === "POA")) {
        destinationSelect.value = "POA";
    }
}

async function highlightAirportConnections(iata) {
    selectedConnections = await getAirportConnections(iata);
    selectedRoute = null;

    const airport = getAirportById(iata);
    const details = document.getElementById("node-details");
    const routeResult = document.getElementById("route-result");

    if (routeResult) {
        routeResult.innerHTML = "";
    }

    const conexoesOrdenadas = [...selectedConnections.conexoes].sort((a, b) => {
        return Number(a.peso) - Number(b.peso);
    });

    const lista = conexoesOrdenadas.map(conexao => {
        const destino = getAirportById(conexao.destino);
        const destinoTexto = destino
            ? `${conexao.destino} — ${destino.cidade}`
            : conexao.destino;

        return `
            <li>
                <strong>${conexao.origem} → ${destinoTexto}</strong><br>
                Distância aproximada: ${Number(conexao.peso).toFixed(1)} km<br>
                Tipo: ${conexao.tipo_conexao}
            </li>
        `;
    }).join("");

    details.classList.remove("empty-state");
    details.innerHTML = `
        <div class="airport-summary">
            <strong>${iata}</strong>
            <span>Grau ${selectedConnections.grau}</span>
        </div>

        <div class="detail-grid">
            <div class="detail-item">
                <small>Cidade</small>
                <strong>${airport?.cidade || "-"}</strong>
            </div>

            <div class="detail-item">
                <small>Região</small>
                <strong>${airport?.regiao || "-"}</strong>
            </div>

            <div class="detail-item">
                <small>Densidade ego</small>
                <strong>${Number(airport?.densidade_ego || 0).toFixed(4)}</strong>
            </div>

            <div class="detail-item">
                <small>Conexões</small>
                <strong>${selectedConnections.conexoes.length}</strong>
            </div>
        </div>

        <p>
            Conexões diretas ordenadas pela menor distância aproximada:
        </p>

        <ul>${lista}</ul>
    `;

    renderMap();
}

async function highlightRoute() {
    const origem = document.getElementById("route-origin").value;
    const destino = document.getElementById("route-destination").value;

    if (origem === destino) {
        alert("Origem e destino devem ser diferentes.");
        return;
    }

    if (selectedRegion !== "TODAS") {
        selectedRegion = "TODAS";
        currentFocus = "BRASIL";

        const regionFilter = document.getElementById("region-filter");

        if (regionFilter) {
            regionFilter.value = "TODAS";
        }
    }

    selectedRoute = await calculateRoute(origem, destino);
    selectedConnections = null;

    document.getElementById("node-details").classList.add("empty-state");
    document.getElementById("node-details").innerHTML = `
        Nenhum aeroporto selecionado.
        <br />
        A rota calculada está destacada em vermelho no mapa.
    `;

    document.getElementById("route-result").innerHTML = `
        <div class="route-summary">
            <strong>${origem} → ${destino}</strong>
            <span>${Number(selectedRoute.custo).toFixed(2)} km</span>
        </div>

        <p><strong>Caminho mínimo:</strong></p>

        <div class="route-path">
            ${selectedRoute.caminho.map(item => `<span>${item}</span>`).join("<i>→</i>")}
        </div>
    `;

    renderMap();
}

async function setQuickRoute(origem, destino) {
    document.getElementById("route-origin").value = origem;
    document.getElementById("route-destination").value = destino;
    await highlightRoute();
}

function clearHighlights() {
    selectedRoute = null;
    selectedConnections = null;

    const details = document.getElementById("node-details");
    details.classList.add("empty-state");
    details.innerHTML = `
        Nenhum aeroporto selecionado.
        <br />
        Clique em um ponto no mapa para visualizar cidade, região, grau e conexões diretas.
    `;

    document.getElementById("route-result").innerHTML = "";

    renderMap();
}

function applyRegionFilter(region) {
    selectedRegion = region;
    currentFocus = regionToFocus[region] || "BRASIL";
    clearHighlights();
}

function toggleBaseEdges() {
    showBaseEdges = !showBaseEdges;

    const button = document.getElementById("btn-toggle-edges");

    if (button) {
        button.textContent = showBaseEdges
            ? "Ocultar conexões fixas"
            : "Mostrar conexões fixas";
    }

    renderMap();
}

function focusRegion(focusKey) {
    currentFocus = focusKey;
    renderMap();
}
