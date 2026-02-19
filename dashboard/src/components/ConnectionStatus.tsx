import React from 'react';

interface ConnectionStatusProps {
  isConnected: boolean;
  isError: boolean;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ isConnected, isError }) => {
  const getStatusColor = () => {
    if (isError) return 'bg-red-500';
    if (isConnected) return 'bg-green-500';
    return 'bg-yellow-500';
  };

  const getStatusText = () => {
    if (isError) return 'Error';
    if (isConnected) return 'Conectado';
    return 'Conectando...';
  };

  return (
    <div className="flex items-center gap-2">
      <div className={`w-3 h-3 rounded-full ${getStatusColor()} animate-pulse`} />
      <span className="text-sm font-medium text-gray-700">{getStatusText()}</span>
    </div>
  );
};
