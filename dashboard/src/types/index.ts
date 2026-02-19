// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
  timestamp: string;
  request_id: string;
}

// Variable Types
export interface Variable {
  variable_id: string;
  name: string;
  area: 'pre-treatment' | 'e-coat' | 'production-control';
  unit: string;
  data_type: string;
  min_range: number;
  max_range: number;
  alarm_low: number;
  alarm_high: number;
  description: string;
  active: boolean;
}

// Sensor Data Types
export interface SensorData {
  variable_id: string;
  area: string;
  timestamp: string;
  value: number;
  unit: string;
  quality: string;
  metadata: {
    min_range: number;
    max_range: number;
    alarm_low: number;
    alarm_high: number;
  };
}

// Alarm Types
export type AlarmSeverity = 'warning' | 'critical';
export type AlarmStatus = 'active' | 'acknowledged' | 'resolved';

export interface Alarm {
  alarm_id: string;
  variable_id: string;
  area: string;
  severity: AlarmSeverity;
  status: AlarmStatus;
  message: string;
  value: number;
  threshold: number;
  created_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
  acknowledged_by?: string;
}

// Statistics Types
export interface Statistics {
  variable_id: string;
  window_start: string;
  window_end: string;
  window_minutes: number;
  count: number;
  avg: number;
  min: number;
  max: number;
  stddev: number;
}
