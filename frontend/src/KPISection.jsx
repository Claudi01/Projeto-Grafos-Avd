import React from 'react';
import { TrendingUp, Plane, Network, BarChart3, Gauge } from 'lucide-react';
import KPICard from './KPICard';

/**
 * Seção com grid de 5 KPIs
 */
const KPISection = ({ kpis }) => {
  const colors = {
    traffic: '#1f77b4',      // Azul
    airports: '#2ca02c',     // Verde
    hub: '#ff7f0e',         // Laranja
    peak: '#d62728',        // Vermelho
    density: '#9467bd',     // Roxo
  };

  return (
    <div className="kpi-section">
      <KPICard
        icon={TrendingUp}
        label="Tráfego Total"
        value={kpis.totalPassageiros}
        unit=" M"
        color={colors.traffic}
      />
      <KPICard
        icon={Plane}
        label="Aeroportos Conectados"
        value={kpis.totalAeroportos}
        unit=""
        color={colors.airports}
      />
      <KPICard
        icon={Network}
        label="Maior Hub (Grau)"
        value={kpis.hubNome}
        unit={` (${kpis.hubGrau})`}
        color={colors.hub}
      />
      <KPICard
        icon={BarChart3}
        label="Maior Tráfego"
        value={kpis.picoNome}
        unit={` (${kpis.picoPassageiros}M)`}
        color={colors.peak}
      />
      <KPICard
        icon={Gauge}
        label="Métrica Extra"
        value="—"
        unit=""
        color={colors.density}
      />
    </div>
  );
};

export default KPISection;
