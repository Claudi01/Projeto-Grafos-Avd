import { useState, useCallback } from 'react';

/**
 * Hook para gerenciar estado interativo global do dashboard
 * Controla filtros, seleções e hovers
 */
export const useInteractiveState = () => {
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [hoveredAirport, setHoveredAirport] = useState(null);
  const [selectedAirports, setSelectedAirports] = useState([]);
  const [filterGradeRange, setFilterGradeRange] = useState([0, 100]);
  const [filterPassengerRange, setFilterPassengerRange] = useState([0, 1000]);

  // Limpar seleção
  const clearFilters = useCallback(() => {
    setSelectedRegion(null);
    setSelectedAirports([]);
    setHoveredAirport(null);
    setFilterGradeRange([0, 100]);
    setFilterPassengerRange([0, 1000]);
  }, []);

  // Toggle de seleção múltipla
  const toggleAirportSelection = useCallback((iata) => {
    setSelectedAirports(prev =>
      prev.includes(iata) ? prev.filter(a => a !== iata) : [...prev, iata]
    );
  }, []);

  return {
    selectedRegion,
    setSelectedRegion,
    hoveredAirport,
    setHoveredAirport,
    selectedAirports,
    toggleAirportSelection,
    filterGradeRange,
    setFilterGradeRange,
    filterPassengerRange,
    setFilterPassengerRange,
    clearFilters,
  };
};
