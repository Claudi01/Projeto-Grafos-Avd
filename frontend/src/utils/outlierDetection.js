/**
 * Detecção de outliers usando IQR (Interquartile Range)
 */

import { calculateStats } from './graphMetrics';

/**
 * Identifica outliers por região
 */
export const detectOutliersByRegion = (dados) => {
  const byRegion = {};

  // Agrupar por região
  dados.forEach(d => {
    if (!byRegion[d.regiao]) {
      byRegion[d.regiao] = [];
    }
    byRegion[d.regiao].push(d.passageiros_milhoes);
  });

  // Calcular outliers por região
  const outliers = {};
  const dadosWithOutlier = dados.map(d => {
    const regionValues = byRegion[d.regiao];
    const stats = calculateStats(regionValues);
    const isOutlier = d.passageiros_milhoes < stats.lowerBound || 
                      d.passageiros_milhoes > stats.upperBound;
    
    if (isOutlier) {
      if (!outliers[d.regiao]) outliers[d.regiao] = [];
      outliers[d.regiao].push(d);
    }

    return {
      ...d,
      isOutlier,
      regionStats: stats,
    };
  });

  return { dadosWithOutlier, outliers, byRegion };
};

/**
 * Gera dados para Boxplot (Plotly)
 * Retorna um array com um boxplot por região
 */
export const generateBoxplotData = (dados) => {
  const byRegion = {};

  dados.forEach(d => {
    if (!byRegion[d.regiao]) {
      byRegion[d.regiao] = [];
    }
    byRegion[d.regiao].push(d.passageiros_milhoes);
  });

  const traces = Object.keys(byRegion).map(region => ({
    y: byRegion[region],
    name: region,
    type: 'box',
    boxmean: 'sd',
  }));

  return traces;
};

/**
 * Identifica outliers globais
 */
export const detectGlobalOutliers = (dados, field = 'passageiros_milhoes') => {
  const values = dados.map(d => d[field]);
  const stats = calculateStats(values);

  return dados.filter(d => 
    d[field] < stats.lowerBound || d[field] > stats.upperBound
  );
};
