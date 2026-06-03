import { useState, useEffect } from 'react';

/**
 * Hook customizado para carregar dados do dashboard
 * Faz fetch do JSON e calcula KPIs básicos
 */
export const useDashboardData = () => {
  const [dados, setDados] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [kpis, setKpis] = useState({
    totalPassageiros: 0,
    totalAeroportos: 0,
    hubNome: '-',
    hubGrau: 0,
    picoNome: '-',
    picoPassageiros: 0,
  });

  useEffect(() => {
    const fetchDados = async () => {
      try {
        setLoading(true);
        const response = await fetch('/dados_dashboard.json');
        if (!response.ok) throw new Error('Erro ao carregar dados');
        
        const data = await response.json();
        setDados(data);

        // Cálculos de KPIs básicos
        const totalPass = data.reduce((acc, curr) => acc + (curr.passageiros_milhoes || 0), 0);
        const conectados = data.filter(d => d.grau > 0).length;
        
        let maxGrau = 0;
        let hubIata = '-';
        let maxPass = 0;
        let picoIata = '-';

        data.forEach(d => {
          if (d.grau > maxGrau) {
            maxGrau = d.grau;
            hubIata = d.iata;
          }
          if (d.passageiros_milhoes > maxPass) {
            maxPass = d.passageiros_milhoes;
            picoIata = d.iata;
          }
        });

        setKpis({
          totalPassageiros: totalPass.toFixed(1),
          totalAeroportos: conectados,
          hubNome: hubIata,
          hubGrau: maxGrau,
          picoNome: picoIata,
          picoPassageiros: maxPass.toFixed(1),
        });

        setError(null);
      } catch (err) {
        console.error('Erro ao carregar dados:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDados();
  }, []);

  return { dados, loading, error, kpis };
};
