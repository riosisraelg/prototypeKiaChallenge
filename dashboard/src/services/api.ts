import axios, { AxiosInstance, AxiosError } from 'axios';
import type { ApiResponse, Variable, SensorData, Alarm, Statistics } from '../types';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:3000';
    const apiKey = process.env.REACT_APP_API_KEY || '';

    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
      },
      timeout: 30000,
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response) {
          // Server responded with error
          console.error('API Error:', error.response.status, error.response.data);
        } else if (error.request) {
          // Request made but no response
          console.error('Network Error:', error.message);
        } else {
          // Error in request setup
          console.error('Request Error:', error.message);
        }
        return Promise.reject(error);
      }
    );
  }

  // GET /variables - List all variables
  async getVariables(): Promise<Variable[]> {
    const response = await this.client.get<ApiResponse<Variable[]>>('/variables');
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || 'Failed to fetch variables');
  }

  // GET /variables/{id}/data - Get variable data
  async getVariableData(
    variableId: string,
    start: string,
    end: string
  ): Promise<SensorData[]> {
    const response = await this.client.get<ApiResponse<SensorData[]>>(
      `/variables/${variableId}/data`,
      {
        params: { start, end },
      }
    );
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || 'Failed to fetch variable data');
  }

  // GET /alarms - List alarms
  async getAlarms(status?: 'active' | 'acknowledged' | 'resolved'): Promise<Alarm[]> {
    const response = await this.client.get<ApiResponse<Alarm[]>>('/alarms', {
      params: status ? { status } : {},
    });
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || 'Failed to fetch alarms');
  }

  // POST /alarms/{id}/acknowledge - Acknowledge alarm
  async acknowledgeAlarm(alarmId: string): Promise<Alarm> {
    const response = await this.client.post<ApiResponse<Alarm>>(
      `/alarms/${alarmId}/acknowledge`
    );
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || 'Failed to acknowledge alarm');
  }

  // GET /statistics/{variable_id} - Get statistics
  async getStatistics(variableId: string): Promise<Statistics[]> {
    const response = await this.client.get<ApiResponse<Statistics[]>>(
      `/statistics/${variableId}`
    );
    if (response.data.success && response.data.data) {
      return response.data.data;
    }
    throw new Error(response.data.error?.message || 'Failed to fetch statistics');
  }
}

export const apiClient = new ApiClient();
