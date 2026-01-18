// API Configuration
export const API_CONFIG = {
  // Default to localhost for development
  // Change to your Railway URL in production
  BASE_URL: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000',

  // API Endpoints
  ENDPOINTS: {
    // Auth
    LOGIN: '/api/v1/auth/login',
    REGISTER: '/api/v1/auth/register',
    REFRESH: '/api/v1/auth/refresh',
    ME: '/api/v1/auth/me',

    // Portfolio
    PORTFOLIO: '/api/v1/portfolio',
    BALANCE: '/api/v1/portfolio/balance',

    // Market
    TICKER: '/api/v1/market/ticker',
    OHLCV: '/api/v1/market/ohlcv',

    // Trades
    TRADES: '/api/v1/trades',

    // Bot
    BOT_START: '/api/v1/bot/start',
    BOT_STOP: '/api/v1/bot/stop',
    BOT_PAUSE: '/api/v1/bot/pause',
    BOT_RESUME: '/api/v1/bot/resume',
    BOT_STATUS: '/api/v1/bot/status',
    BOT_TRADES: '/api/v1/bot/trades',
    BOT_PERFORMANCE: '/api/v1/bot/performance',

    // Strategies
    STRATEGIES: '/api/v1/strategies',

    // Health
    HEALTH: '/health',
  },

  // Timeouts
  TIMEOUT: 10000,

  // WebSocket
  WS_URL: process.env.EXPO_PUBLIC_WS_URL || 'ws://localhost:8000/ws',
};

export default API_CONFIG;
