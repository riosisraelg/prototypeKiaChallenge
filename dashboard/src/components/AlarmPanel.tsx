import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAlarms } from '../hooks/useVariableData';
import { apiClient } from '../services/api';
import type { Alarm, AlarmStatus } from '../types';

export const AlarmPanel: React.FC = () => {
  const [statusFilter, setStatusFilter] = useState<AlarmStatus>('active');
  const { data: alarms, isLoading, isError } = useAlarms(statusFilter);
  const queryClient = useQueryClient();

  const acknowledgeMutation = useMutation({
    mutationFn: (alarmId: string) => apiClient.acknowledgeAlarm(alarmId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alarms'] });
    },
  });

  const getSeverityColor = (severity: string) => {
    return severity === 'critical' ? 'bg-red-100 border-red-500' : 'bg-yellow-100 border-yellow-500';
  };

  const getSeverityBadge = (severity: string) => {
    return severity === 'critical'
      ? 'bg-red-500 text-white'
      : 'bg-yellow-500 text-white';
  };

  const handleAcknowledge = (alarmId: string) => {
    acknowledgeMutation.mutate(alarmId);
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <div className="text-red-600">Error al cargar alarmas</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-800">Alarmas</h3>
          <span className="text-sm text-gray-500">{alarms?.length || 0} alarmas</span>
        </div>
        <div className="flex gap-2">
          {(['active', 'acknowledged', 'resolved'] as AlarmStatus[]).map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                statusFilter === status
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {status === 'active' && 'Activas'}
              {status === 'acknowledged' && 'Reconocidas'}
              {status === 'resolved' && 'Resueltas'}
            </button>
          ))}
        </div>
      </div>
      <div className="overflow-y-auto max-h-[400px]">
        {alarms && alarms.length > 0 ? (
          <div className="divide-y">
            {alarms.map((alarm) => (
              <div
                key={alarm.alarm_id}
                className={`p-4 border-l-4 ${getSeverityColor(alarm.severity)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span
                        className={`px-2 py-1 rounded text-xs font-bold ${getSeverityBadge(
                          alarm.severity
                        )}`}
                      >
                        {alarm.severity.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500">{alarm.variable_id}</span>
                    </div>
                    <p className="text-sm text-gray-800 mb-1">{alarm.message}</p>
                    <div className="text-xs text-gray-500">
                      <div>
                        Valor: {alarm.value.toFixed(2)} | Umbral: {alarm.threshold.toFixed(2)}
                      </div>
                      <div>
                        {new Date(alarm.created_at).toLocaleString('es-ES')}
                      </div>
                    </div>
                  </div>
                  {alarm.status === 'active' && (
                    <button
                      onClick={() => handleAcknowledge(alarm.alarm_id)}
                      disabled={acknowledgeMutation.isPending}
                      className="ml-4 px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                    >
                      {acknowledgeMutation.isPending ? 'Procesando...' : 'Reconocer'}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-gray-500">
            No hay alarmas {statusFilter === 'active' && 'activas'}
            {statusFilter === 'acknowledged' && 'reconocidas'}
            {statusFilter === 'resolved' && 'resueltas'}
          </div>
        )}
      </div>
    </div>
  );
};
