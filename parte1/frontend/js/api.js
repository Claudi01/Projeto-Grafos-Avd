const API_BASE = "";

async function apiGet(endpoint) {
    const response = await fetch(`${API_BASE}${endpoint}`);

    if (!response.ok) {
        throw new Error(`Erro na API: ${endpoint}`);
    }

    return await response.json();
}

async function getGraphData() {
    return await apiGet("/api/grafo");
}

async function getGlobalMetrics() {
    return await apiGet("/api/metricas/global");
}

async function getDegrees() {
    return await apiGet("/api/metricas/graus");
}

async function getRegions() {
    return await apiGet("/api/metricas/regioes");
}

async function getEgoMetrics() {
    return await apiGet("/api/metricas/ego");
}

async function getDistances() {
    return await apiGet("/api/distancias");
}

async function getInsights() {
    return await apiGet("/api/insights");
}

async function calculateRoute(origem, destino) {
    return await apiGet(`/api/rotas?origem=${origem}&destino=${destino}`);
}

async function getAirportConnections(iata) {
    return await apiGet(`/api/aeroportos/${iata}/conexoes`);
}
async function getPassengers() {
    return await apiGet("/api/passageiros");
}

async function getPassengerAnalytics() {
    return await apiGet("/api/analytics/passageiros");
}
