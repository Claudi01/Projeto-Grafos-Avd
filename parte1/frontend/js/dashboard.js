let chartInstances = [];

async function initDashboard() {
    destroyExistingCharts();

    const graus = await getDegrees();
    const ego = await getEgoMetrics();
    const passageirosAnalytics = await getPassengerAnalytics();

    renderDegreesChart(graus);
    renderPassengersRankingChart(passageirosAnalytics.ranking_passageiros);
    renderPassengersByRegionChart(passageirosAnalytics.passageiros_por_regiao);
    renderDegreePassengersChart(passageirosAnalytics.grau_x_passageiros);
    renderPassengersPerConnectionChart(passageirosAnalytics.passageiros_por_conexao);
    renderEgoChart(ego);
}

function destroyExistingCharts() {
    for (const chart of chartInstances) {
        chart.destroy();
    }

    chartInstances = [];
}

function getCanvas(id) {
    const canvas = document.getElementById(id);

    if (!canvas) {
        console.warn(`Canvas não encontrado: ${id}`);
        return null;
    }

    return canvas;
}

function pushChart(chart) {
    if (chart) {
        chartInstances.push(chart);
    }
}

function renderDegreesChart(data) {
    const canvas = getCanvas("chart-degrees");

    if (!canvas) {
        return;
    }

    const sorted = [...data]
        .sort((a, b) => Number(b.grau) - Number(a.grau))
        .slice(0, 10);

    const chart = new Chart(canvas, {
        type: "bar",
        data: {
            labels: sorted.map(item => item.aeroporto),
            datasets: [{
                label: "Grau",
                data: sorted.map(item => Number(item.grau)),
                backgroundColor: "#3b82f6",
                borderColor: "#bfdbfe",
                borderWidth: 1
            }]
        },
        options: chartOptions("Grau dos aeroportos", false)
    });

    pushChart(chart);
}

function renderPassengersRankingChart(data) {
    const canvas = getCanvas("chart-passengers-ranking");

    if (!canvas) {
        return;
    }

    const sorted = [...data]
        .sort((a, b) => Number(b.passageiros_milhoes) - Number(a.passageiros_milhoes))
        .slice(0, 10);

    const chart = new Chart(canvas, {
        type: "bar",
        data: {
            labels: sorted.map(item => item.iata),
            datasets: [{
                label: "Passageiros em milhões",
                data: sorted.map(item => Number(item.passageiros_milhoes)),
                backgroundColor: "#f97316",
                borderColor: "#fed7aa",
                borderWidth: 1
            }]
        },
        options: chartOptions("Ranking de passageiros", true)
    });

    pushChart(chart);
}

function renderPassengersByRegionChart(data) {
    const canvas = getCanvas("chart-passengers-region");

    if (!canvas) {
        return;
    }

    const sorted = [...data]
        .sort((a, b) => Number(b.passageiros_milhoes) - Number(a.passageiros_milhoes));

    const chart = new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: sorted.map(item => item.regiao),
            datasets: [{
                label: "Passageiros em milhões",
                data: sorted.map(item => Number(item.passageiros_milhoes)),
                backgroundColor: [
                    "#3b82f6",
                    "#f97316",
                    "#22c55e",
                    "#a855f7",
                    "#e11d48"
                ],
                borderColor: "#0f172a",
                borderWidth: 2
            }]
        },
        options: doughnutOptions()
    });

    pushChart(chart);
}

function renderDegreePassengersChart(data) {
    const canvas = getCanvas("chart-degree-passengers");

    if (!canvas) {
        return;
    }

    const points = data.map(item => ({
        x: Number(item.grau),
        y: Number(item.passageiros_milhoes),
        iata: item.iata,
        cidade: item.cidade,
        regiao: item.regiao
    }));

    const chart = new Chart(canvas, {
        type: "scatter",
        data: {
            datasets: [{
                label: "Aeroportos",
                data: points,
                backgroundColor: "#22c55e",
                borderColor: "#bbf7d0",
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: scatterOptions(
            "Grau",
            "Passageiros em milhões",
            context => {
                const item = context.raw;
                return `${item.iata} — Grau ${item.x}; ${item.y.toFixed(1)} mi passageiros`;
            }
        )
    });

    pushChart(chart);
}

function renderPassengersPerConnectionChart(data) {
    const canvas = getCanvas("chart-passengers-per-connection");

    if (!canvas) {
        return;
    }

    const sorted = [...data]
        .sort((a, b) => Number(b.passageiros_por_conexao) - Number(a.passageiros_por_conexao))
        .slice(0, 10);

    const chart = new Chart(canvas, {
        type: "bar",
        data: {
            labels: sorted.map(item => item.iata),
            datasets: [{
                label: "Milhões de passageiros por conexão direta",
                data: sorted.map(item => Number(item.passageiros_por_conexao)),
                backgroundColor: "#06b6d4",
                borderColor: "#cffafe",
                borderWidth: 1
            }]
        },
        options: chartOptions("Passageiros por conexão direta", true)
    });

    pushChart(chart);
}

function renderEgoChart(data) {
    const canvas = getCanvas("chart-ego");

    if (!canvas) {
        return;
    }

    const sorted = [...data]
        .sort((a, b) => Number(b.densidade_ego) - Number(a.densidade_ego))
        .slice(0, 10);

    const chart = new Chart(canvas, {
        type: "bar",
        data: {
            labels: sorted.map(item => item.aeroporto),
            datasets: [{
                label: "Densidade ego",
                data: sorted.map(item => Number(item.densidade_ego)),
                backgroundColor: "#a855f7",
                borderColor: "#e9d5ff",
                borderWidth: 1
            }]
        },
        options: chartOptions("Top densidade ego", false, 0, 1)
    });

    pushChart(chart);
}

function chartOptions(title, beginAtZero = true, min = undefined, max = undefined) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: "#e5e7eb"
                }
            },
            title: {
                display: false,
                text: title,
                color: "#e5e7eb"
            }
        },
        scales: {
            x: {
                ticks: {
                    color: "#e5e7eb"
                },
                grid: {
                    color: "rgba(148, 163, 184, 0.15)"
                }
            },
            y: {
                beginAtZero: beginAtZero,
                min: min,
                max: max,
                ticks: {
                    color: "#e5e7eb"
                },
                grid: {
                    color: "rgba(148, 163, 184, 0.15)"
                }
            }
        }
    };
}

function doughnutOptions() {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: "bottom",
                labels: {
                    color: "#e5e7eb"
                }
            },
            tooltip: {
                callbacks: {
                    label: context => {
                        const label = context.label || "";
                        const value = Number(context.raw).toFixed(1);
                        return `${label}: ${value} mi passageiros`;
                    }
                }
            }
        }
    };
}

function scatterOptions(xTitle, yTitle, tooltipLabelCallback) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: "#e5e7eb"
                }
            },
            tooltip: {
                callbacks: {
                    label: tooltipLabelCallback
                }
            }
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: xTitle,
                    color: "#e5e7eb"
                },
                ticks: {
                    color: "#e5e7eb"
                },
                grid: {
                    color: "rgba(148, 163, 184, 0.15)"
                }
            },
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: yTitle,
                    color: "#e5e7eb"
                },
                ticks: {
                    color: "#e5e7eb"
                },
                grid: {
                    color: "rgba(148, 163, 184, 0.15)"
                }
            }
        }
    };
}
