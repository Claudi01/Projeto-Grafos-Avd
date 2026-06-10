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

function formatNumber(value, decimalPlaces = 1) {
    return Number(value).toLocaleString("pt-BR", {
        minimumFractionDigits: decimalPlaces,
        maximumFractionDigits: decimalPlaces
    });
}

function renderInsights(insights) {
    const container = document.getElementById("insights-container");

    if (!container) {
        return;
    }

    const graus = insights.ranking_graus ?? {};
    const passageiros = insights.ranking_passageiros ?? {};
    const regiao = insights.passageiros_por_regiao ?? {};
    const correlacao = insights.grau_x_passageiros ?? {};
    const porConexao = insights.passageiros_por_conexao ?? {};
    const ego = insights.densidade_ego ?? {};

    const aeroportosForaDoGrafo = regiao.aeroportos_fora_do_grafo?.length
        ? regiao.aeroportos_fora_do_grafo.join(", ")
        : "nenhum";

    const aeroportosEmpatados = ego.aeroportos_empatados?.length
        ? ego.aeroportos_empatados.join(", ")
        : "-";

    container.innerHTML = `
        ${createInsightCard(
            "1. Ranking de graus",
            `
                <b>${graus.aeroporto ?? "-"}</b> lidera com grau
                <b>${graus.grau ?? "-"}</b>, equivalente a
                <b>${formatNumber(graus.percentual_conexoes ?? 0)}%</b> das conexões
                diretas possíveis.
                <br><br>
                ${graus.interpretacao ?? "O grau identifica os principais hubs estruturais da rede."}
            `
        )}

        ${createInsightCard(
            "2. Ranking de passageiros",
            `
                <b>${passageiros.aeroporto ?? "-"}</b> movimenta
                <b>${formatNumber(passageiros.passageiros_milhoes ?? 0)} milhões</b> de passageiros,
                <b>${formatNumber(passageiros.diferenca_milhoes ?? 0)} milhões</b> acima de
                ${passageiros.segundo_aeroporto ?? "-"}.
                <br><br>
                ${passageiros.interpretacao ?? "O ranking evidencia os aeroportos de maior relevância operacional."}
            `
        )}

        ${createInsightCard(
            "3. Passageiros por região",
            `
                A região <b>${regiao.regiao ?? "-"}</b> soma
                <b>${formatNumber(regiao.passageiros_milhoes ?? 0)} milhões</b> de passageiros,
                ou <b>${formatNumber(regiao.participacao_percentual ?? 0)}%</b> do total analisado.
                <br><br>
                ${regiao.interpretacao ?? "A distribuição regional mostra onde o tráfego da rede está concentrado."}
                Foram considerados ${regiao.aeroportos_considerados ?? "-"} aeroportos do grafo;
                registros fora dele: ${aeroportosForaDoGrafo}.
            `
        )}

        ${createInsightCard(
            "4. Grau x passageiros",
            `
                O coeficiente de correlação é
                <b>${formatNumber(correlacao.correlacao ?? 0, 4)}</b>, indicando associação
                positiva <b>${correlacao.intensidade ?? "-"}</b>.
                <br><br>
                ${correlacao.interpretacao ?? "A comparação avalia a relação entre conectividade e movimentação de passageiros."}
            `
        )}

        ${createInsightCard(
            "5. Passageiros por conexão direta",
            `
                <b>${porConexao.aeroporto ?? "-"}</b> lidera com
                <b>${formatNumber(porConexao.passageiros_por_conexao ?? 0)} milhões</b> de passageiros
                por conexão, a partir de grau <b>${porConexao.grau ?? "-"}</b>.
                <br><br>
                ${porConexao.interpretacao ?? "A razão destaca aeroportos com alto tráfego em relação ao número de conexões modeladas."}
            `
        )}

        ${createInsightCard(
            "6. Top densidade ego",
            `
                A maior densidade ego é <b>${formatNumber(ego.densidade_ego ?? 0)}</b>.
                <b>${ego.aeroporto_destaque ?? "-"}</b> se destaca entre os empatados
                por possuir grau <b>${ego.grau_destaque ?? "-"}</b>.
                <br><br>
                ${ego.interpretacao ?? "A densidade ego mede a conectividade da vizinhança local."}
                Empatados: ${aeroportosEmpatados}.
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
