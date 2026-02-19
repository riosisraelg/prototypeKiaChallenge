import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import type { Variable, SensorData, Alarm, Statistics } from '../types';

// Hook for fetching all variables
export function useVariables() {
  return useQuery<Variable[], Error>({
    queryKey: ['variables'],
    queryFn: () => apiClient.getVariables(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 30000, // Auto-refresh every 30 seconds
  });
}

// Hook for fetching variable data
export function useVariableData(
  variableId: string | null,
  start: string,
  end: string,
  enabled: boolean = true
) {
  return useQuery<SensorData[], Error>({
    queryKey: ['variableData', variableId, start, end],
    queryFn: () => {
      if (!variableId) throw new Error('Variable ID is required');
      return apiClient.getVariableData(variableId, start, end);
    },
    enabled: enabled && !!variableId,
    staleTime: 10000, // 10 seconds
    refetchInterval: 30000, // Auto-refresh every 30 seconds
  });
}

// Hook for fetching alarms
export function useAlarms(status?: 'active' | 'acknowledged' | 'resolved') {
  return useQuery<Alarm[], Error>({
    queryKey: ['alarms', status],
    queryFn: () => apiClient.getAlarms(status),
    staleTime: 10000, // 10 seconds
    refetchInterval: 30000, // Auto-refresh every 30 seconds
  });
}

// Hook for fetching statistics
export function useStatistics(variableId: string | null, enabled: boolean = true) {
  return useQuery<Statistics[], Error>({
    queryKey: ['statistics', variableId],
    queryFn: () => {
      if (!variableId) throw new Error('Variable ID is required');
      return apiClient.getStatistics(variableId);
    },
    enabled: enabled && !!variableId,
    staleTime: 30000, // 30 seconds
    refetchInterval: 30000, // Auto-refresh every 30 seconds
  });
}
