import React from 'react';

/**
 * Spinner de carregamento
 */
const LoadingSpinner = ({ message = 'Carregando dados...' }) => {
  return (
    <div className="loading-container">
      <div className="spinner"></div>
      <p>{message}</p>
    </div>
  );
};

export default LoadingSpinner;
