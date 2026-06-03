import React from 'react';
import { X } from 'lucide-react';

/**
 * Painel de filtros interativos
 */
const FilterPanel = ({
  regions = [],
  selectedRegion,
  onRegionChange,
  onClearFilters,
}) => {
  return (
    <div className="filter-panel">
      <div className="filter-header">
        <h3>Filtros</h3>
        {selectedRegion && (
          <button className="clear-btn" onClick={onClearFilters}>
            <X size={18} /> Limpar
          </button>
        )}
      </div>

      <div className="filter-group">
        <label htmlFor="region-select">Região</label>
        <select
          id="region-select"
          value={selectedRegion || ''}
          onChange={(e) => onRegionChange(e.target.value || null)}
        >
          <option value="">Todas as regiões</option>
          {regions.map(region => (
            <option key={region} value={region}>
              {region}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default FilterPanel;
