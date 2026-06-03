import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';

/**
 * Gráfico de Dispersão: Grau vs Passageiros
 * Visualiza relação entre conectividade estrutural e tráfego real
 */
const ScatterChart = ({ data, selectedRegion, hoveredAirport, onHover, baseLayout }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !data || data.length === 0) return;

    // Filtrar por região se selecionada
    const filtrados = selectedRegion
      ? data.filter(d => d.regiao === selectedRegion && d.passageiros_milhoes > 0)
      : data.filter(d => d.passageiros_milhoes > 0);

    const colors = {
      'Norte': '#2ca02c',
      'Nordeste': '#ff7f0e',
      'Centro-Oeste': '#d62728',
      'Sudeste': '#1f77b4',
      'Sul': '#9467bd',
      'Desconhecida': '#7f8c8d',
    };

    // Customizar opacidade baseado em hover
    const getOpacity = (iata) => {
      if (!hoveredAirport) return 0.8;
      return iata === hoveredAirport ? 1 : 0.3;
    };

    const getSize = (iata) => {
      if (!hoveredAirport) return Math.max((filtrados.find(d => d.iata === iata)?.passageiros_milhoes || 1) * 1.5, 5);
      return iata === hoveredAirport ? 15 : 5;
    };

    const plotData = [{
      x: filtrados.map(d => d.grau),
      y: filtrados.map(d => d.passageiros_milhoes),
      mode: 'markers+text',
      text: filtrados.map(d => d.iata),
      textposition: 'top center',
      textfont: { size: 9, color: '#e2e8f0' },
      marker: {
        size: filtrados.map(d => getSize(d.iata)),
        color: filtrados.map(d => colors[d.regiao]),
        line: { width: 2, color: 'white' },
        opacity: filtrados.map(d => getOpacity(d.iata)),
      },
      hovertemplate: '<b>%{text}</b><br>Grau: %{x}<br>Passageiros: %{y:.2f}M<extra></extra>',
      type: 'scatter',
    }];

    const layout = {
      ...baseLayout,
      title: `Dispersão: Grau vs Passageiros${selectedRegion ? ` (${selectedRegion})` : ''}`,
      xaxis: { title: 'Grau (Conectividade)' },
      yaxis: { title: 'Passageiros (Milhões)' },
      hovermode: 'closest',
      height: 400,
    };

    Plotly.newPlot(containerRef.current, plotData, layout, { displayModeBar: false, responsive: true });

    const handleHover = (data) => {
      if (data.points && data.points.length > 0) {
        onHover?.(data.points[0].text);
      }
    };

    const handleUnhover = () => {
      onHover?.(null);
    };

    containerRef.current.on('plotly_hover', handleHover);
    containerRef.current.on('plotly_unhover', handleUnhover);

    return () => {
      if (containerRef.current) {
        containerRef.current.removeListener('plotly_hover', handleHover);
        containerRef.current.removeListener('plotly_unhover', handleUnhover);
      }
    };
  }, [data, selectedRegion, hoveredAirport, onHover, baseLayout]);

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />;
};

export default ScatterChart;
