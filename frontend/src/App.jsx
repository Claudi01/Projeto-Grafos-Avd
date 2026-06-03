import React, { useState } from 'react';
import { LayoutDashboard, Network } from 'lucide-react';
import { useDashboardData } from './hooks/useDashboardData';
import { useMetricsCalculation } from './hooks/useMetricsCalculation';
import { useInteractiveState } from './hooks/useInteractiveState';
import KPISection from './KPISection';
import LoadingSpinner from './LoadingSpinner';
import FilterPanel from './FilterPanel';
import ScatterChart from './charts/ScatterChart';
import RegionalBarChart from './charts/RegionalBarChart';
import TreemapChart from './charts/TreemapChart';
import Top10BarChart from './charts/Top10BarChart';
import EgoNetworkScatter from './charts/EgoNetworkScatter';
import BoxplotChart from './charts/BoxplotChart';
import './App.css';

/**
 * App Principal - Dashboard Interativo de Aviação
 * Integra KPIs, gráficos e filtros interativos
 */
function App() {
  const [activeTab, setActiveTab] = useState('avd');
  const { dados, loading, error, kpis } = useDashboardData();
  const metrics = useMetricsCalculation(dados);
  const {
    selectedRegion,
    setSelectedRegion,
    hoveredAirport,
    setHoveredAirport,
    clearFilters,
  } = useInteractiveState();

  // Config base para todos os gráficos
  const baseLayout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: '#e2e8f0', family: 'Inter' },
    margin: { l: 40, r: 20, t: 40, b: 40 },
    autosize: true,
  };

  // Extrair regiões únicas para filtro
  const regioes = [...new Set(dados.map(d => d.regiao))].sort();

  // Estado de carregamento/erro
  if (loading) return <LoadingSpinner message="Carregando dados da rede de aviação..." />;
  if (error) return <div style={{ color: '#ef4444', textAlign: 'center', marginTop: '20%' }}>Erro: {error}</div>;
  if (dados.length === 0) return <LoadingSpinner message="Nenhum dado disponível" />;

  return (
    <div className="app-container">
      <header>
        <h1>Plataforma Analítica: Aviação</h1>
        <p>Sistema de visualização de grafos - Análise de Conectividade e Tráfego</p>
      </header>

      {/* ABAS */}
      <div className="tab-container">
        <button
          className={`tab-btn ${activeTab === 'avd' ? 'active' : ''}`}
          onClick={() => setActiveTab('avd')}
        >
          <LayoutDashboard size={18} /> Painel Analítico
        </button>
        <button
          className={`tab-btn ${activeTab === 'grafo' ? 'active' : ''}`}
          onClick={() => setActiveTab('grafo')}
        >
          <Network size={18} /> Malha Interativa
        </button>
      </div>

      {/* PAINEL ANALÍTICO */}
      {activeTab === 'avd' && (
        <div className="avd-container">
          {/* Filtros */}
          <section className="filter-section">
            <FilterPanel
              regions={regioes}
              selectedRegion={selectedRegion}
              onRegionChange={setSelectedRegion}
              onClearFilters={clearFilters}
            />
          </section>

          {/* KPIs em destaque */}
          <section className="kpi-section-wrapper">
            <KPISection kpis={kpis} />
          </section>

          {/* Grid de Gráficos - 6 visualizações */}
          <section className="charts-section">
            <div className="chart-grid">
              {/* Gráfico 1: Dispersão */}
              <div className="chart-card">
                <h3>Grau vs Passageiros</h3>
                <ScatterChart
                  data={dados}
                  selectedRegion={selectedRegion}
                  hoveredAirport={hoveredAirport}
                  onHover={setHoveredAirport}
                  baseLayout={baseLayout}
                />
              </div>

              {/* Gráfico 2: Barras por Região */}
              <div className="chart-card">
                <h3>Tráfego por Região</h3>
                <RegionalBarChart
                  data={dados}
                  selectedRegion={selectedRegion}
                  baseLayout={baseLayout}
                />
              </div>

              {/* Gráfico 3: Treemap */}
              <div className="chart-card">
                <h3>Hierarquia: Região → Cidade → Aeroporto</h3>
                <TreemapChart
                  data={dados}
                  baseLayout={baseLayout}
                />
              </div>

              {/* Gráfico 4: Top 10 */}
              <div className="chart-card">
                <h3>Top 10 Aeroportos</h3>
                <Top10BarChart
                  data={dados}
                  baseLayout={baseLayout}
                />
              </div>

              {/* Gráfico 5: Ego-Network */}
              <div className="chart-card">
                <h3>Densidade Ego-Network vs Tráfego</h3>
                <EgoNetworkScatter
                  data={dados}
                  baseLayout={baseLayout}
                />
              </div>

              {/* Gráfico 6: Boxplot */}
              <div className="chart-card">
                <h3>Distribuição por Região (Outliers)</h3>
                <BoxplotChart
                  data={dados}
                  baseLayout={baseLayout}
                />
              </div>
            </div>
          </section>
        </div>
      )}

      {/* MALHA INTERATIVA */}
      {activeTab === 'grafo' && (
        <div className="iframe-container">
          <iframe src="/grafo_interativo.html" title="Grafo Interativo"></iframe>
        </div>
      )}
    </div>
  );
}

export default App;