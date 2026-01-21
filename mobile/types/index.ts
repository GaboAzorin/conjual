// User and Auth types
export interface User {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
}

// Portfolio types
export interface Portfolio {
  id: number;
  user_id: number;
  exchange: string;
  total_value_clp: number;
  total_value_usd: number;
  btc_balance: number;
  clp_balance: number;
  created_at: string;
  updated_at: string;
}

export interface Balance {
  clp: number;
  btc: number;
  total_clp: number;
  btc_price_clp: number;
}

// Trade types
export interface Trade {
  id: number;
  portfolio_id: number;
  symbol: string;
  side: 'buy' | 'sell';
  amount: number;
  price: number;
  fee: number;
  total: number;
  status: string;
  executed_at: string;
  created_at: string;
}

// Bot types
export interface BotStatus {
  status: string;
  strategy: string;
  is_paper_trading: boolean;
  uptime_seconds: number;
  paper_trading_stats?: PaperTradingStats;
}

export interface PaperTradingStats {
  initial_balance_clp: number;
  current_balance_clp: number;
  btc_balance: number;
  total_trades: number;
  avg_buy_price: number;
  current_btc_value_clp: number;
  total_value_clp: number;
  profit_loss_clp: number;
  profit_loss_pct: number;
}

export interface BotPerformance {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  total_profit_clp: number;
  total_profit_pct: number;
  avg_trade_profit: number;
  max_drawdown: number;
}

// Market types
export interface Ticker {
  symbol: string;
  price: number;
  volume_24h: number;
  change_24h: number;
  high_24h: number;
  low_24h: number;
}

export interface OHLCV {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// Strategy types
export interface Strategy {
  id: string;
  name: string;
  description: string;
  parameters: Record<string, unknown>;
  is_active: boolean;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface ApiError {
  detail: string;
  status_code: number;
}
