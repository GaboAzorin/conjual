import api from './api';
import { API_CONFIG } from '@/constants/api';
import { BotStatus, BotPerformance, Trade } from '@/types';

export interface StartBotParams {
  paper_trading?: boolean;
  strategy?: string;
  initial_balance?: number;
}

export const botService = {
  async start(params: StartBotParams = { paper_trading: true }): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>(
      API_CONFIG.ENDPOINTS.BOT_START,
      params
    );
    return response.data;
  },

  async stop(): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>(
      API_CONFIG.ENDPOINTS.BOT_STOP
    );
    return response.data;
  },

  async pause(): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>(
      API_CONFIG.ENDPOINTS.BOT_PAUSE
    );
    return response.data;
  },

  async resume(): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>(
      API_CONFIG.ENDPOINTS.BOT_RESUME
    );
    return response.data;
  },

  async getStatus(): Promise<BotStatus> {
    const response = await api.get<BotStatus>(API_CONFIG.ENDPOINTS.BOT_STATUS);
    return response.data;
  },

  async getTrades(limit: number = 50): Promise<Trade[]> {
    const response = await api.get<{ trades: Trade[] }>(API_CONFIG.ENDPOINTS.BOT_TRADES, {
      params: { limit },
    });
    return response.data.trades || [];
  },

  async getPerformance(): Promise<BotPerformance> {
    const response = await api.get<BotPerformance>(
      API_CONFIG.ENDPOINTS.BOT_PERFORMANCE
    );
    return response.data;
  },
};

export default botService;
