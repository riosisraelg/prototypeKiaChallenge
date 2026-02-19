import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { useVariableData } from '../hooks/useVariableData';
import type { Variable } from '../types';

interface VariableChartProps {
  variable: Variable | null;
}

export const VariableChart: React.FC<VariableChartProps> = ({ variable }) => {
  // Calculate time range: last 60 minutes
  const { start, end } = useMemo(() => {
    const now = new Date();
    const sixtyMinutesAgo = new Date(now.getTime() - 60 * 60 * 1000);
    return {
      start: sixtyMinutesAgo.toISOString(),
      end: now.toISOString(),
    };
  }, []);

  const { data: sensorData, isLoading, isError } = useVariableData(
    variable?.variable_id || null,
    start,
    end,
    !!variable
  );

  const chartData = useMemo(() => {
    if (!sensorData) return [];
    return sensorData.map((d) => ({
      timestamp: new Date(d.timestamp).toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit',
      }),
      value: d.value,
      fullTimestamp: d.timestamp,
    }));
  }, [sensorData]);

  if (!variable) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <div className="text-gray-500 text-center py-12">
          Selecciona una variable para ver el gráfico
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <div className="text-red-600">Error al cargar datos</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800">{variable.name}</h3>
        <p className="text-sm text-gray-500">
          {variable.variable_id} - Últimos 60 minutos
        </p>
      </div>
      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="timestamp"
              tick={{ fontSize: 12 }}
              interval="preserveStartEnd"
            />
            <YAxis
              domain={[variable.min_range * 0.9, variable.max_range * 1.1]}
              tick={{ fontSize: 12 }}
              label={{ value: variable.unit, angle: -90, position: 'insideLeft' }}
            />
            <Tooltip
              contentStyle={{ backgroundColor: 'white', border: '1px solid #ccc' }}
              labelStyle={{ fontWeight: 'bold' }}
            />
            <Legend />
            <ReferenceLine
              y={variable.alarm_high}
              stroke="red"
              strokeDasharray="3 3"
              label={{ value: 'Alarma Alta', position: 'right', fontSize: 10 }}
            />
            <ReferenceLine
              y={variable.alarm_low}
              stroke="orange"
              strokeDasharray="3 3"
              label={{ value: 'Alarma Baja', position: 'right', fontSize: 10 }}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#2563eb"
              strokeWidth={2}
              dot={false}
              name={`Valor (${variable.unit})`}
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div className="text-gray-500 text-center py-12">
          No hay datos disponibles para este período
        </div>
      )}
    </div>
  );
};
