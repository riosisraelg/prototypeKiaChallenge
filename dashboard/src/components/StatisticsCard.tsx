import React from 'react';
import { useStatistics } from '../hooks/useVariableData';

interface StatisticsCardProps {
  variableId: string | null;
  unit: string;
}

export const StatisticsCard: React.FC<StatisticsCardProps> = ({ variableId, unit }) => {
  const { data: statistics, isLoading, isError } = useStatistics(variableId, !!variableId);

  const latestStats = statistics && statistics.length > 0 ? statistics[0] : null;

  const formatValue = (value: number | undefined) => {
    if (value === undefined || value === null) return 'N/A';
    return value.toFixed(2);
  };

  if (!variableId) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <div className="text-gray-500 text-center">Selecciona una variable</div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-2 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <div className="text-red-600 text-sm">Error al cargar estadísticas</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Estadísticas</h3>
      {latestStats ? (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-blue-50 rounded-lg p-3">
            <div className="text-xs text-gray-600 mb-1">Promedio</div>
            <div className="text-2xl font-bold text-blue-600">
              {formatValue(latestStats.avg)}
            </div>
            <div className="text-xs text-gray-500">{unit}</div>
          </div>
          <div className="bg-green-50 rounded-lg p-3">
            <div className="text-xs text-gray-600 mb-1">Mínimo</div>
            <div className="text-2xl font-bold text-green-600">
              {formatValue(latestStats.min)}
            </div>
            <div className="text-xs text-gray-500">{unit}</div>
          </div>
          <div className="bg-orange-50 rounded-lg p-3">
            <div className="text-xs text-gray-600 mb-1">Máximo</div>
            <div className="text-2xl font-bold text-orange-600">
              {formatValue(latestStats.max)}
            </div>
            <div className="text-xs text-gray-500">{unit}</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-3">
            <div className="text-xs text-gray-600 mb-1">Desv. Est.</div>
            <div className="text-2xl font-bold text-purple-600">
              {formatValue(latestStats.stddev)}
            </div>
            <div className="text-xs text-gray-500">{unit}</div>
          </div>
        </div>
      ) : (
        <div className="text-gray-500 text-center py-8">No hay datos disponibles</div>
      )}
      {latestStats && (
        <div className="mt-4 text-xs text-gray-500">
          Ventana: {latestStats.window_minutes} min | Muestras: {latestStats.count}
        </div>
      )}
    </div>
  );
};
