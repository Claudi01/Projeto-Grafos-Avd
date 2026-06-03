import React, { useState, useEffect } from 'react';
import Plotly from 'plotly.js-dist-min';
import reactPlotlyFactory from 'react-plotly.js/factory';
import { LayoutDashboard, Network } from 'lucide-react';
import './App.css';

// Importação segura do Plotly para o Vite
const buildPlot = typeof reactPlotlyFactory === 'function' ? reactPlotlyFactory : reactPlotlyFactory.default;
const Plot = buildPlot(Plotly);

function App() {
  const [activeTab, setActiveTab] = useState('avd');
  const [dados, setDados] = useState([]);
  const [kpis, setKpis] = useState({ totalPassageiros: 0, totalAeroportos: 0, hubNome: "-", hubGrau: 0, picoNome: "-" });

  // 1. Carrega o JSON que o Python gerou assim que a página abre
  useEffect(() => {
    fetch('/dados_dashboard.json')
      .then(response => response.json())
      .then(data => {
        setDados(data);
        
        // Calcula os KPIs no próprio navegador instantaneamente
        const passageiros = data.reduce((acc, curr) => acc + (curr.passageiros_milhoes || 0), 0);
        const conectados = data.filter(d => d.grau > 0).length;
        
        let maxGrau = 0; let hubIata = "-";
        let maxPass = 0; let picoIata = "-";
        
        data.forEach(d => {
          if (d.grau > maxGrau) { maxGrau = d.grau; hubIata = d.iata; }
          if (d.passageiros_milhoes > maxPass) { maxPass = d.passageiros_milhoes; picoIata = d.iata; }
        });

        setKpis({ totalPassageiros: passageiros.toFixed(1), totalAeroportos: conectados, hubNome: hubIata, hubGrau: maxGrau, picoNome: picoIata });
      })
      .catch(err => console.error("Erro ao carregar dados:", err));
  }, []);

  // Paleta de Cores Gestalt
  const colors = { 'Norte': '#2ca02c', 'Nordeste': '#ff7f0e', 'Centro-Oeste': '#d62728', 'Sudeste': '#1f77b4', 'Sul': '#9467bd', 'Desconhecida': '#7f8c8d' };
  
  // Layout base para todos os gráficos (transparente e com texto branco)
  const baseLayout = {
    paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: "#e2e8f0", family: "Inter" },
    margin: { l: 40, r: 20, t: 40, b: 40 },
    autosize: true
  };

  // Processamento rápido para os gráficos
  const getGraficoBarrasRegiao = () => {
    const regioes = {};
    dados.forEach(d => {
      regioes[d.regiao] = (regioes[d.regiao] || 0) + d.passageiros_milhoes;
    });
    return {
      x: Object.values(regioes), y: Object.keys(regioes), type: 'bar', orientation: 'h',
      marker: { color: Object.keys(regioes).map(r => colors[r]) }
    };
  };

  const getScatterChart = () => {
    const filtrados = dados.filter(d => d.passageiros_milhoes > 0);
    return {
      x: filtrados.map(d => d.grau), y: filtrados.map(d => d.passageiros_milhoes),
      mode: 'markers', text: filtrados.map(d => d.iata),
      marker: { size: filtrados.map(d => Math.max(d.passageiros_milhoes * 1.5, 5)), color: filtrados.map(d => colors[d.regiao]), line: {width: 1, color: 'white'}, opacity: 0.8 }
    };
  };

  const getTop10Chart = () => {
    const top10 = [...dados].sort((a, b) => b.passageiros_milhoes - a.passageiros_milhoes).slice(0, 10).reverse();
    return {
      x: top10.map(d => d.passageiros_milhoes), y: top10.map(d => d.iata), type: 'bar', orientation: 'h',
      marker: { color: top10.map(d => d.grau), colorscale: 'Viridis' }
    };
  };

  if (dados.length === 0) return <div style={{color: 'white', textAlign: 'center', marginTop: '20%'}}>Carregando a super aplicação...</div>;

  return (
    <div className="app-container">
      <header>
        <h1>Plataforma Analítica: Aviação</h1>
        <p>Dashboard de Alta Performance (React + Python)</p>
      </header>

      <div className="tab-container">
        <button className={`tab-btn ${activeTab === 'avd' ? 'active' : ''}`} onClick={() => setActiveTab('avd')}>
          <LayoutDashboard size={20} /> Painel Analítico (AVD)
        </button>
        <button className={`tab-btn ${activeTab === 'grafo' ? 'active' : ''}`} onClick={() => setActiveTab('grafo')}>
          <Network size={20} /> Malha Interativa (Grafos)
        </button>
      </div>

      {activeTab === 'avd' && (
        <>
          <div className="kpi-container">
            <div className="kpi-card"><div className="kpi-title">Tráfego Total</div><div className="kpi-value">{kpis.totalPassageiros} <span>Milhões</span></div></div>
            <div className="kpi-card"><div className="kpi-title">Aeroportos Conectados</div><div className="kpi-value">{kpis.totalAeroportos} <span>Nós</span></div></div>
            <div className="kpi-card"><div className="kpi-title">Maior Hub</div><div className="kpi-value">{kpis.hubNome} <span>({kpis.hubGrau} rotas)</span></div></div>
            <div className="kpi-card"><div className="kpi-title">Pico de Tráfego</div><div className="kpi-value">{kpis.picoNome}</div></div>
          </div>

          <div className="chart-grid">
            <div className="chart-card">
              <Plot data={[getGraficoBarrasRegiao()]} layout={{...baseLayout, title: "Tráfego por Região"}} useResizeHandler style={{width: '100%', height: '100%'}} config={{displayModeBar: false}} />
            </div>
            <div className="chart-card">
              <Plot data={[getScatterChart()]} layout={{...baseLayout, title: "Conexões vs Passageiros"}} useResizeHandler style={{width: '100%', height: '100%'}} config={{displayModeBar: false}} />
            </div>
            <div className="chart-card" style={{gridColumn: 'span 2'}}>
              <Plot data={[getTop10Chart()]} layout={{...baseLayout, title: "Top 10 Aeroportos (Cor = Conexões)"}} useResizeHandler style={{width: '100%', height: '100%'}} config={{displayModeBar: false}} />
            </div>
          </div>
        </>
      )}

      {activeTab === 'grafo' && (
        <div className="iframe-container">
          <iframe src="/grafo_interativo.html" title="Grafo Interativo"></iframe>
        </div>
      )}
    </div>
  );
}

export default App;