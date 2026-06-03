import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';

/**
 * Gráfico: Top 10 Aeroportos
 * Barras horizontais dos 10 maiores aeroportos, coloridas por grau
 */
const Top10BarChart = ({ data, baseLayout }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !data || data.length === 0) return;

    // Top 10 por passageiros
    const top10 = data
      .filter(d => d.passageiros_milhoes > 0)
      .sort((a, b) => b.passageiros_milhoes - a.passageiros_milhoes)
      .slice(0, 10);

    // Mapear grau para cor (gradiente de azul)
    const getColorByGrade = (grau, maxGrau) => {
      const intensity = grau / maxGrau;
      const r = Math.round(31 + (200 - 31) * intensity);
      const g = Math.round(119 + (119 - 119) * intensity);
      const b = Math.round(180 - (100 * intensity));
      return `rgb(${r}, ${g}, ${b})`;
    };

    const maxGrau = Math.max(...top10.map(d => d.grau));

    const plotData = [{
      x: top10.map(d => d.passageiros_milhoes),
      y: top10.map(d => d.iata),
      type: 'bar',
      orientation: 'h',
      marker: {
        color: top10.map(d => getColorByGrade(d.grau, maxGrau)),
        line: { color: 'white', width: 1 },
      },
      customdata: top10.map(d => d.grau),
      hovertemplate: '<b>%{y}</b><br>Passageiros: %{x:.2f}M<br>Grau: %{customdata}<extra></extra>',
    }];

    const layout = {
      ...baseLayout,
      title: 'Top 10 Aeroportos (Colorido por Grau)',
      xaxis: { title: 'Passageiros (Milhões)' },
      yaxis: { title: 'Aeroporto' },
      height: 400,
    };

    Plotly.newPlot(containerRef.current, plotData, layout, { displayModeBar: false, responsive: true });
  }, [data, baseLayout]);

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />;
};

export default Top10BarChart;
