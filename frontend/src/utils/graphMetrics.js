/**
 * Utilitários para cálculos de métricas de grafos
 */

/**
 * Calcula densidade de uma ego-network (vizinhos de um nó)
 * Densidade = arestas_reais / arestas_possíveis
 */
export const calculateEgoNetworkDensity = (node, allNodes) => {
  if (!node || node.grau === 0) return 0;

  // Simplicidade: usar grau como proxy
  // Em uma rede real, seria contar edges entre vizinhos
  const maxConnections = node.grau * (node.grau - 1) / 2;
  if (maxConnections === 0) return 0;

  // Retornar uma densidade simplificada (0 a 1)
  return Math.min(node.grau / (allNodes.length - 1), 1);
};

/**
 * Calcula betweenness centrality simplificada
 * Proxy: usar grau normalizado
 */
export const calculateBetweennessCentrality = (node, allNodes) => {
  if (!allNodes || allNodes.length === 0) return 0;
  return (node.grau || 0) / (allNodes.length - 1);
};

/**
 * Calcula closeness centrality
 * Proxy: usar grau (nós com maior grau estão "mais pertos" de todos)
 */
export const calculateClosenessCentrality = (node, allNodes) => {
  if (!allNodes || allNodes.length === 0) return 0;
  const maxGrau = Math.max(...allNodes.map(n => n.grau || 0));
  return maxGrau > 0 ? (node.grau || 0) / maxGrau : 0;
};

/**
 * Filtra dados com base em critérios
 */
export const filterData = (dados, { region, gradeMin, gradeMax, passengerMin, passengerMax }) => {
  return dados.filter(d => {
    if (region && d.regiao !== region) return false;
    if (d.grau < gradeMin || d.grau > gradeMax) return false;
    if (d.passageiros_milhoes < passengerMin || d.passageiros_milhoes > passengerMax) return false;
    return true;
  });
};

/**
 * Calcula estatísticas descritivas
 */
export const calculateStats = (array) => {
  if (!array || array.length === 0) return {};
  
  const sorted = [...array].sort((a, b) => a - b);
  const n = sorted.length;
  const mean = sorted.reduce((a, b) => a + b, 0) / n;
  
  const q1 = sorted[Math.floor(n * 0.25)];
  const median = sorted[Math.floor(n * 0.5)];
  const q3 = sorted[Math.floor(n * 0.75)];
  const iqr = q3 - q1;
  
  return {
    min: sorted[0],
    q1,
    median,
    q3,
    max: sorted[n - 1],
    mean: mean.toFixed(2),
    iqr,
    lowerBound: q1 - 1.5 * iqr,
    upperBound: q3 + 1.5 * iqr,
  };
};

/**
 * Detecta outliers (valores fora de [Q1 - 1.5*IQR, Q3 + 1.5*IQR])
 */
export const findOutliers = (array) => {
  const stats = calculateStats(array);
  return array.filter(val => val < stats.lowerBound || val > stats.upperBound);
};
