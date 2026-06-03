import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';

/**
 * Gráfico de Barras Horizontal: Tráfego por Região
 * Visualiza distribuição de passageiros entre regiões
 */
const RegionalBarChart = ({ data, selectedRegion, baseLayout }) => {
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
    const porRegiao = {};
    data.forEach(d => {
      porRegiao[d.regiao] = (porRegiao[d.regiao] || 0) + d.passageiros_milhoes;
    });

    const regioes = Object.keys(porRegiao).sort();
    const valores = regioes.map(r => porRegiao[r]);
    const coresPorRegiao = regioes.map(r => colors[r]);

    const plotData = [{
      x: valores,
      y: regioes,
      type: 'bar',
      orientation: 'h',
      marker: {
        color: coresPorRegiao,
        line: { color: 'white', width: 1 },
      },
      hovertemplate: '<b>%{y}</b><br>Tráfego: %{x:.2f}M<extra></extra>',
    }];

    const layout = {
      ...baseLayout,
      title: 'Tráfego Total por Região',
      xaxis: { title: 'Passageiros (Milhões)' },
      yaxis: { title: 'Região' },
      hovermode: 'closest',
      height: 400,
    };

    Plotly.newPlot(containerRef.current, plotData, layout, { displayModeBar: false, responsive: true });
  }, [data, selectedRegion, baseLayout]);

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />;
};

export default RegionalBarChart;
