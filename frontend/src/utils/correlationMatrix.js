/**
 * Cálculo de correlação de Pearson
 * Implementação simplificada sem dependências externas
 */

export const calculatePearsonCorrelation = (x, y) => {
  if (!x || !y || x.length !== y.length || x.length === 0) return 0;

  const n = x.length;
  const meanX = x.reduce((a, b) => a + b, 0) / n;
  const meanY = y.reduce((a, b) => a + b, 0) / n;

  let numerator = 0;
  let sumX2 = 0;
  let sumY2 = 0;

  for (let i = 0; i < n; i++) {
    const dx = x[i] - meanX;
    const dy = y[i] - meanY;
    numerator += dx * dy;
    sumX2 += dx * dx;
    sumY2 += dy * dy;
  }

  const denominator = Math.sqrt(sumX2 * sumY2);
  return denominator === 0 ? 0 : (numerator / denominator).toFixed(3);
};

/**
 * Gera matriz de correlação entre múltiplas variáveis
 * @param dados Array de objetos
 * @param variaveis Array com nomes das variáveis
 */
export const generateCorrelationMatrix = (dados, variaveis) => {
  if (!dados || dados.length === 0) return {};

  const matrix = {};
  
  for (let i = 0; i < variaveis.length; i++) {
    matrix[variaveis[i]] = {};
    const x = dados.map(d => d[variaveis[i]] || 0);

    for (let j = 0; j < variaveis.length; j++) {
      const y = dados.map(d => d[variaveis[j]] || 0);
      matrix[variaveis[i]][variaveis[j]] = calculatePearsonCorrelation(x, y);
    }
  }

  return matrix;
};

/**
 * Converte matriz de correlação para formato de Plotly heatmap
 */
export const correlationMatrixToHeatmap = (matrix) => {
  if (!matrix || Object.keys(matrix).length === 0) return { z: [], x: [], y: [] };

  const labels = Object.keys(matrix);
  const z = labels.map(label => labels.map(col => parseFloat(matrix[label][col])));

  return {
    z,
    x: labels,
    y: labels,
  };
};
