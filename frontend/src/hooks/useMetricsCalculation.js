import { useMemo } from 'react';

/**
 * Hook para calcular métricas complexas com memoização
 * Evita recálculos desnecessários
 */
export const useMetricsCalculation = (dados) => {
  const metrics = useMemo(() => {
    if (!dados || dados.length === 0) return {};

    // Densidade média da rede
    const totalGrau = dados.reduce((acc, d) => acc + (d.grau || 0), 0);
    const numeroNos = dados.filter(d => d.grau > 0).length;
    const densidadeMedia = numeroNos > 1 ? (totalGrau / (numeroNos * (numeroNos - 1))).toFixed(4) : 0;

    // Top 10 aeroportos
    const top10 = dados
      .filter(d => d.passageiros_milhoes > 0)
      .sort((a, b) => b.passageiros_milhoes - a.passageiros_milhoes)
      .slice(0, 10);

    // Agrupamento por região
    const porRegiao = {};
    dados.forEach(d => {
      if (!porRegiao[d.regiao]) {
        porRegiao[d.regiao] = {
          passageiros: 0,
          aeroportos: 0,
          grauMedio: 0,
          aeroportosList: [],
        };
      }
      porRegiao[d.regiao].passageiros += d.passageiros_milhoes;
      porRegiao[d.regiao].aeroportos += 1;
      porRegiao[d.regiao].grauMedio += d.grau;
      porRegiao[d.regiao].aeroportosList.push(d);
    });

    // Calcular grau médio por região
    Object.keys(porRegiao).forEach(regiao => {
      porRegiao[regiao].grauMedio = 
        porRegiao[regiao].aeroportos > 0 
          ? (porRegiao[regiao].grauMedio / porRegiao[regiao].aeroportos).toFixed(2)
          : 0;
    });

    return {
      densidadeMedia,
      top10,
      porRegiao,
    };
  }, [dados]);

  return metrics;
};
