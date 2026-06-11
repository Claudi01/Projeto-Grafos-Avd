function safeElement(id) {
    return document.getElementById(id);
}

function updateMapStatus(text) {
    const status = safeElement("map-dynamic-status");

    if (status) {
        status.textContent = text;
    }
}

function bindGraphPageEvents() {
    const calculateRouteButton = safeElement("btn-calculate-route");
    const recPoaButton = safeElement("btn-rec-poa");
    const maoGruButton = safeElement("btn-mao-gru");
    const clearButton = safeElement("btn-clear-highlight");
    const regionFilter = safeElement("region-filter");
    const toggleEdgesButton = safeElement("btn-toggle-edges");

    if (calculateRouteButton && typeof highlightRoute === "function") {
        calculateRouteButton.addEventListener("click", () => {
            highlightRoute();
            updateMapStatus("Rota calculada");
        });
    }

    if (recPoaButton && typeof setQuickRoute === "function") {
        recPoaButton.addEventListener("click", () => {
            setQuickRoute("REC", "POA");
            updateMapStatus("Rota REC → POA");
        });
    }

    if (maoGruButton && typeof setQuickRoute === "function") {
        maoGruButton.addEventListener("click", () => {
            setQuickRoute("MAO", "GRU");
            updateMapStatus("Rota MAO → GRU");
        });
    }

    if (clearButton && typeof clearHighlights === "function") {
        clearButton.addEventListener("click", () => {
            clearHighlights();
            updateMapStatus("Mapa interativo");
        });
    }

    if (regionFilter && typeof renderMap === "function") {
        regionFilter.addEventListener("change", function () {
            try {
                selectedRegion = this.value;
            } catch (error) {
                console.warn("Filtro de região indisponível.", error);
            }

            if (typeof clearHighlights === "function") {
                clearHighlights();
            }

            renderMap();

            const label = this.value === "TODAS"
                ? "Todas as regiões"
                : `Região ${this.value}`;

            updateMapStatus(label);
        });
    }

    if (toggleEdgesButton && typeof renderMap === "function") {
        toggleEdgesButton.addEventListener("click", function () {
            try {
                showBaseEdges = !showBaseEdges;

                this.textContent = showBaseEdges
                    ? "Ocultar conexões fixas"
                    : "Mostrar conexões fixas";

                renderMap();

                updateMapStatus(
                    showBaseEdges
                        ? "Conexões fixas visíveis"
                        : "Conexões fixas ocultas"
                );
            } catch (error) {
                console.warn("Controle de conexões indisponível.", error);
            }
        });
    }

    bindFocusButton("btn-focus-brasil", "BRASIL", "Brasil inteiro");
    bindFocusButton("btn-focus-norte", "NORTE", "Foco: Norte");
    bindFocusButton("btn-focus-nordeste", "NORDESTE", "Foco: Nordeste");
    bindFocusButton("btn-focus-centro", "CENTRO-OESTE", "Foco: Centro-Oeste");
    bindFocusButton("btn-focus-sudeste", "SUDESTE", "Foco: Sudeste");
    bindFocusButton("btn-focus-sul", "SUL", "Foco: Sul");
}

function bindFocusButton(buttonId, regionKey, statusText) {
    const button = safeElement(buttonId);

    if (!button || typeof focusRegion !== "function") {
        return;
    }

    button.addEventListener("click", () => {
        focusRegion(regionKey);
        updateMapStatus(statusText);
    });
}

window.addEventListener("DOMContentLoaded", async () => {
    try {
        if (typeof initMap !== "function") {
            throw new Error("Função initMap não encontrada.");
        }

        await initMap();
        bindGraphPageEvents();
    } catch (error) {
        console.error(error);
        alert("Erro ao carregar o grafo. Verifique se a API Flask está em execução e se os dados foram gerados.");
    }
});