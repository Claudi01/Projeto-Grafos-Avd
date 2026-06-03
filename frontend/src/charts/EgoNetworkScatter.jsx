import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';
import { calculateEgoNetworkDensity } from '../utils/graphMetrics';

/**
 * Gráfico: Densidade Ego-Network vs Tráfego
 * Scatter: eixo X = densidade local, eixo Y = passageiros
 * Para provar: redes fechadas recebem mais ou menos voos?
 */
const EgoNetworkScatter = ({ data, baseLayout }) => {
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

    // Calcular densidade de ego-network para cada aeroporto
    const filtrados = data.filter(d => d.passageiros_milhoes > 0 && d.grau > 0);

    const densidades = filtrados.map(d => ({
      ...d,
      egoDensity: calculateEgoNetworkDensity(d, data),
    }));

    const plotData = [{
      x: densidades.map(d => d.egoDensity),
      y: densidades.map(d => d.passageiros_milhoes),
      mode: 'markers',
      text: densidades.map(d => d.iata),
      marker: {
        size: densidades.map(d => Math.max(d.grau * 0.8, 5)),
        color: densidades.map(d => colors[d.regiao]),
        line: { width: 1, color: 'white' },
        opacity: 0.7,
      },
      hovertemplate: '<b>%{text}</b><br>Densidade Ego: %{x:.3f}<br>Passageiros: %{y:.2f}M<extra></extra>',
      type: 'scatter',
    }];

    const layout = {
      ...baseLayout,
      title: 'Densidade da Ego-Network vs Tráfego',
      xaxis: { title: 'Densidade Local (0-1)' },
      yaxis: { title: 'Passageiros (Milhões)' },
      hovermode: 'closest',
      height: 400,
    };

    Plotly.newPlot(containerRef.current, plotData, layout, { displayModeBar: false, responsive: true });
  }, [data, baseLayout]);

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />;
};

export default EgoNetworkScatter;
