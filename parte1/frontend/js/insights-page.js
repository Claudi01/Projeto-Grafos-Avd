async function fetchJson(url) {
    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`Erro ao buscar ${url}`);
    }

    return response.json();
}

function createInsightCard(title, body) {
    return `
        <div class="insight-card">
            <strong>${title}</strong>
            <p>${body}</p>
        </div>
    `;
}

function renderInsights(insights) {
    const container = document.getElementById("insights-container");

    if (!container) {
        return;
    }

    const estrutura = insights.estrutura_global ?? {};
    const hub = insights.hub_principal ?? {};
    const regiao = insights.regiao_mais_densa ?? {};
    const ego = insights.maior_densidade_ego ?? {};

    container.innerHTML = `
        ${createInsightCard(
            "Estrutura global da rede",
            `
                O grafo possui <b>${estrutura.ordem ?? "-"}</b> aeroportos,
                <b>${estrutura.tamanho ?? "-"}</b> conexões e densidade
                <b>${estrutura.densidade ?? "-"}</b>.
                <br><br>
                ${estrutura.interpretacao ?? "A métrica de densidade permite avaliar o nível geral de conectividade da rede."}
            `
        )}

        ${createInsightCard(
            "Hub principal",
            `
                O aeroporto <b>${hub.aeroporto ?? "-"}</b> apresentou grau
                <b>${hub.grau ?? "-"}</b>, indicando maior número de conexões diretas.
                <br><br>
                ${hub.interpretacao ?? "Aeroportos com maior grau funcionam como pontos estratégicos de articulação da rede."}
            `
        )}

        ${createInsightCard(
            "Região mais densa",
            `
                A região <b>${regiao.regiao ?? "-"}</b> apresentou densidade
                <b>${regiao.densidade ?? "-"}</b>.
                <br><br>
                ${regiao.interpretacao ?? "A densidade regional indica o nível de conectividade interna entre aeroportos da mesma região."}
            `
        )}

        ${createInsightCard(
            "Maior densidade ego",
            `
                O aeroporto <b>${ego.aeroporto ?? "-"}</b> apresentou densidade ego
                <b>${ego.densidade_ego ?? "-"}</b>.
                <br><br>
                ${ego.interpretacao ?? "A densidade ego mede a conectividade local entre um aeroporto e sua vizinhança direta."}
            `
        )}
    `;
}

window.addEventListener("DOMContentLoaded", async () => {
    try {
        const insights = await fetchJson("/api/insights");
        renderInsights(insights);
    } catch (error) {
        console.error(error);
        alert("Erro ao carregar os insights. Verifique se a API Flask está em execução.");
    }
});