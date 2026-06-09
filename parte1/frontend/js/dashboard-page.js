window.addEventListener("DOMContentLoaded", async () => {
    try {
        if (typeof initDashboard !== "function") {
            throw new Error("Função initDashboard não encontrada.");
        }

        await initDashboard();
    } catch (error) {
        console.error(error);
        alert("Erro ao carregar o dashboard. Verifique se a API Flask está em execução.");
    }
});