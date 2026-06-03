import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';

/**
 * Gráfico Treemap Hierárquico
 * Visualiza: Região → Cidade → Aeroporto (proporcional a passageiros)
 */
const TreemapChart = ({ data, baseLayout }) => {
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

    // Estruturar dados hierárquicos
    const labels = [];
    const parents = [];
    const values = [];
    const markerColors = [];

    // Agrupar por região e cidade
    const porRegiaoCity = {};
    data.forEach(d => {
      // Filtrar valores inválidos
      if (d.passageiros_milhoes <= 0 || !d.iata) return;
      
      const key = `${d.regiao}|${d.cidade || 'Desconhecida'}`;
      if (!porRegiaoCity[key]) {
        porRegiaoCity[key] = [];
      }
      porRegiaoCity[key].push(d);
    });

    const regioes = {};
    Object.keys(porRegiaoCity).forEach(key => {
      const [regiao, cidade] = key.split('|');
      if (!regioes[regiao]) {
        regioes[regiao] = {};
      }
      regioes[regiao][cidade] = porRegiaoCity[key];
    });

    // Nível 0: Root
    labels.push('Brasil');
    parents.push('');
    values.push(0);
    markerColors.push('#ffffff');

    // Adicionar regiões
    Object.keys(regioes).forEach(regiao => {
      const totalRegiao = Object.values(regioes[regiao]).reduce((acc, cidades) => {
        return acc + cidades.reduce((a, c) => a + c.passageiros_milhoes, 0);
      }, 0);

      labels.push(regiao);
      parents.push('Brasil');
      values.push(totalRegiao);
      markerColors.push(colors[regiao]);
    });

    // Adicionar cidades e aeroportos
    Object.keys(regioes).forEach(regiao => {
      Object.keys(regioes[regiao]).forEach(cidade => {
        const aeroportos = regioes[regiao][cidade];
        const totalCidade = aeroportos.reduce((acc, a) => acc + a.passageiros_milhoes, 0);

        labels.push(cidade);
        parents.push(regiao);
        values.push(totalCidade);
        markerColors.push(colors[regiao]);

        // Adicionar aeroportos
        aeroportos.forEach(aeroporto => {
          labels.push(aeroporto.iata);
          parents.push(cidade);
          values.push(aeroporto.passageiros_milhoes);
          markerColors.push(colors[regiao]);
        });
      });
    });

    const plotData = [{
      labels,
      parents,
      values,
      type: 'treemap',
      marker: { colors: markerColors, line: { color: 'white', width: 1 } },
      textposition: 'middle center',
      textfont: { size: 10, color: '#fff' },
      hovertemplate: '<b>%{label}</b><br>Passageiros: %{value:.2f}M<extra></extra>',
    }];

    const layout = {
      ...baseLayout,
      title: 'Hierarquia: Região → Cidade → Aeroporto',
      height: 400,
    };

    Plotly.newPlot(containerRef.current, plotData, layout, { displayModeBar: false, responsive: true });
  }, [data, baseLayout]);

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />;
};

export default TreemapChart;
