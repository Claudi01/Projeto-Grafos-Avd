import React from 'react';

/**
 * Card individual de KPI
 * Exibe ícone, valor e label
 */
const KPICard = ({ icon: Icon, label, value, unit = '', color = '#1f77b4' }) => {
  return (
    <div className="kpi-card" style={{ borderLeft: `4px solid ${color}` }}>
      <div className="kpi-header">
        {Icon && <Icon size={24} color={color} />}
        <span className="kpi-label">{label}</span>
      </div>
      <div className="kpi-value">
        {value}
        {unit && <span className="kpi-unit">{unit}</span>}
      </div>
    </div>
  );
};

export default KPICard;
