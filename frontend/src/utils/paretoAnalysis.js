/**
 * Análise de Pareto (regra 80/20)
 * Identifica quantos itens produzem 80% do resultado
 */

export const calculateParetoAnalysis = (dados, valueField = 'passageiros_milhoes') => {
  if (!dados || dados.length === 0) return { total: 0, items80: [], percentage80: 0 };

  // Ordenar descendente
  const sorted = [...dados]
    .sort((a, b) => (b[valueField] || 0) - (a[valueField] || 0));

  const total = sorted.reduce((acc, d) => acc + (d[valueField] || 0), 0);
  const target80 = total * 0.8;

  let accumulated = 0;
  const items80 = [];

  for (const item of sorted) {
    accumulated += item[valueField] || 0;
    items80.push({
      ...item,
      accumulatedPercentage: ((accumulated / total) * 100).toFixed(1),
    });
    if (accumulated >= target80) break;
  }

  return {
    total: total.toFixed(1),
    items80,
    count80: items80.length,
    percentage80: ((items80.length / sorted.length) * 100).toFixed(1),
  };
};

/**
 * Gera dados para gráfico de Pareto (Plotly)
 */
export const generateParetoChartData = (dados, valueField = 'passageiros_milhoes') => {
  const analysis = calculateParetoAnalysis(dados, valueField);
  
  if (!analysis.items80 || analysis.items80.length === 0) {
    return { x: [], y1: [], y2: [] };
  }

  const x = analysis.items80.map((d, idx) => `${idx + 1}`);
  const y1 = analysis.items80.map(d => parseFloat(d[valueField]) || 0); // Valores individuais
  const y2 = analysis.items80.map(d => parseFloat(d.accumulatedPercentage) || 0); // Acumulado %

  return { x, y1, y2, total: analysis.total };
};
