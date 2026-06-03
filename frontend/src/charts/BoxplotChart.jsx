import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';
import { generateBoxplotData } from '../utils/outlierDetection';

/**
 * Gráfico: Boxplot por Região
 * Mostra distribuição de tráfego por região
 * Detecta outliers claramente (ex: Guarulhos)
 */
const BoxplotChart = ({ data, baseLayout }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !data || data.length === 0) return;

    const colors = {
      'Norte': '#2ca02c',
      'Nordeste': '#ff7f0e',
      'Centro-Oeste': '#d62728',
      'Sudeste': '#1f77b4',
      'Sul': '#9467bd',
      'Desconhecida': '#7f8c8d',
    };

    // Agrupar por região
    const byRegion = {};
    data.forEach(d => {
      if (!byRegion[d.regiao]) {
        byRegion[d.regiao] = [];
      }
      byRegion[d.regiao].push(d.passageiros_milhoes);
    });

    // Criar traces para cada região
    const traces = Object.keys(byRegion)
      .sort()
      .map(region => ({
        y: byRegion[region],
        name: region,
        type: 'box',
        boxmean: 'sd',
        marker: { color: colors[region] },
        line: { color: colors[region] },
      }));

    const layout = {
      ...baseLayout,
      title: 'Distribuição de Tráfego por Região (Outliers)',
      yaxis: { title: 'Passageiros (Milhões)' },
      showlegend: false,
      height: 400,
    };

    Plotly.newPlot(containerRef.current, traces, layout, { displayModeBar: false, responsive: true });
  }, [data, baseLayout]);

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />;
};

export default BoxplotChart;
