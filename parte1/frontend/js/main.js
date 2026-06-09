async function fetchJson(url) {
    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`Erro ao buscar ${url}`);
    }

    return response.json();
}

function formatDensity(value) {
    const numberValue = Number(value);

    if (Number.isNaN(numberValue)) {
        return "-";
    }

    return numberValue.toFixed(4);
}

async function initHomeMetrics() {
    const globalMetrics = await fetchJson("/api/metricas/global");
    const degreeMetrics = await fetchJson("/api/metricas/graus");

    const ordem = globalMetrics.ordem ?? globalMetrics.numero_vertices ?? "-";
    const tamanho = globalMetrics.tamanho ?? globalMetrics.numero_arestas ?? "-";
    const densidade = globalMetrics.densidade ?? "-";

    document.getElementById("metric-ordem").textContent = ordem;
    document.getElementById("metric-tamanho").textContent = tamanho;
    document.getElementById("metric-densidade").textContent = formatDensity(densidade);

    if (Array.isArray(degreeMetrics) && degreeMetrics.length > 0) {
        const orderedDegrees = [...degreeMetrics].sort((a, b) => {
            return Number(b.grau) - Number(a.grau);
        });

        const hub = orderedDegrees[0];

        document.getElementById("metric-hub").textContent = hub.aeroporto ?? hub.iata ?? "-";
        document.getElementById("metric-hub-detail").textContent = `Grau ${hub.grau}`;
    }
}

window.addEventListener("DOMContentLoaded", async () => {
    try {
        await initHomeMetrics();
    } catch (error) {
        console.error(error);
        alert("Erro ao carregar a visão geral. Verifique se a API Flask está em execução.");
    }
});