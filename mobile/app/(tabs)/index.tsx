import { useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { useBotStore, useMarketStore, useAuthStore } from '@/stores';

export default function DashboardScreen() {
  const { user } = useAuthStore();
  const { status, fetchStatus } = useBotStore();
  const { ticker, fetchTicker, isLoading: marketLoading } = useMarketStore();

  useEffect(() => {
    fetchStatus();
    fetchTicker();
  }, []);

  const onRefresh = async () => {
    await Promise.all([fetchStatus(), fetchTicker()]);
  };

  const formatCLP = (value: number) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatBTC = (value: number) => {
    return value.toFixed(8);
  };

  const stats = status?.paper_trading_stats;

  return (
    <ScrollView
      className="flex-1 bg-dark-900"
      refreshControl={
        <RefreshControl refreshing={marketLoading} onRefresh={onRefresh} />
      }
    >
      <View className="p-4">
        {/* Welcome Header */}
        <View className="mb-6">
          <Text className="text-dark-400 text-sm">Bienvenido,</Text>
          <Text className="text-white text-xl font-semibold">
            {user?.email?.split('@')[0] || 'Trader'}
          </Text>
        </View>

        {/* BTC Price Card */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4">
          <View className="flex-row items-center justify-between mb-3">
            <View className="flex-row items-center">
              <View className="w-10 h-10 bg-accent rounded-full items-center justify-center mr-3">
                <FontAwesome name="bitcoin" size={24} color="#0f172a" />
              </View>
              <View>
                <Text className="text-white font-semibold text-lg">Bitcoin</Text>
                <Text className="text-dark-400 text-sm">BTC-CLP</Text>
              </View>
            </View>
            <View className="items-end">
              <Text className="text-white font-bold text-xl">
                {ticker ? formatCLP(ticker.price) : '---'}
              </Text>
              <View className="flex-row items-center">
                <FontAwesome
                  name={ticker && ticker.change_24h >= 0 ? 'caret-up' : 'caret-down'}
                  size={14}
                  color={ticker && ticker.change_24h >= 0 ? '#22c55e' : '#ef4444'}
                />
                <Text
                  className={`ml-1 text-sm ${
                    ticker && ticker.change_24h >= 0 ? 'text-profit' : 'text-loss'
                  }`}
                >
                  {ticker ? `${ticker.change_24h.toFixed(2)}%` : '---'}
                </Text>
              </View>
            </View>
          </View>
        </View>

        {/* Portfolio Card */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4">
          <Text className="text-dark-400 text-sm mb-3">Balance Total</Text>
          <Text className="text-white text-3xl font-bold mb-4">
            {stats ? formatCLP(stats.total_value_clp) : '$20,000'}
          </Text>

          <View className="flex-row justify-between">
            <View className="flex-1 mr-2">
              <View className="bg-dark-700 rounded-xl p-3">
                <Text className="text-dark-400 text-xs mb-1">CLP</Text>
                <Text className="text-white font-semibold">
                  {stats ? formatCLP(stats.current_balance_clp) : '$20,000'}
                </Text>
              </View>
            </View>
            <View className="flex-1 ml-2">
              <View className="bg-dark-700 rounded-xl p-3">
                <Text className="text-dark-400 text-xs mb-1">BTC</Text>
                <Text className="text-white font-semibold">
                  {stats ? formatBTC(stats.btc_balance) : '0.00000000'}
                </Text>
              </View>
            </View>
          </View>
        </View>

        {/* P&L Card */}
        {stats && (
          <View className="bg-dark-800 rounded-2xl p-5 mb-4">
            <Text className="text-dark-400 text-sm mb-3">Rendimiento</Text>
            <View className="flex-row items-center">
              <Text
                className={`text-2xl font-bold ${
                  stats.profit_loss_clp >= 0 ? 'text-profit' : 'text-loss'
                }`}
              >
                {stats.profit_loss_clp >= 0 ? '+' : ''}
                {formatCLP(stats.profit_loss_clp)}
              </Text>
              <View
                className={`ml-3 px-2 py-1 rounded-full ${
                  stats.profit_loss_pct >= 0 ? 'bg-profit/20' : 'bg-loss/20'
                }`}
              >
                <Text
                  className={`text-sm font-semibold ${
                    stats.profit_loss_pct >= 0 ? 'text-profit' : 'text-loss'
                  }`}
                >
                  {stats.profit_loss_pct >= 0 ? '+' : ''}
                  {stats.profit_loss_pct.toFixed(2)}%
                </Text>
              </View>
            </View>
          </View>
        )}

        {/* Bot Status Card */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4">
          <View className="flex-row items-center justify-between mb-4">
            <Text className="text-white font-semibold text-lg">Estado del Bot</Text>
            <View
              className={`px-3 py-1 rounded-full ${
                status?.status === 'running'
                  ? 'bg-profit/20'
                  : status?.status === 'paused'
                  ? 'bg-accent/20'
                  : 'bg-dark-600'
              }`}
            >
              <Text
                className={`text-sm font-semibold ${
                  status?.status === 'running'
                    ? 'text-profit'
                    : status?.status === 'paused'
                    ? 'text-accent'
                    : 'text-dark-400'
                }`}
              >
                {status?.status === 'running'
                  ? 'Activo'
                  : status?.status === 'paused'
                  ? 'Pausado'
                  : 'Detenido'}
              </Text>
            </View>
          </View>

          <View className="flex-row justify-between">
            <View>
              <Text className="text-dark-400 text-xs">Estrategia</Text>
              <Text className="text-white">{status?.strategy || 'Smart DCA'}</Text>
            </View>
            <View>
              <Text className="text-dark-400 text-xs">Trades</Text>
              <Text className="text-white">{stats?.total_trades || 0}</Text>
            </View>
            <View>
              <Text className="text-dark-400 text-xs">Modo</Text>
              <Text className="text-accent">
                {status?.is_paper_trading ? 'Paper' : 'Real'}
              </Text>
            </View>
          </View>
        </View>

        {/* Quick Actions */}
        <View className="flex-row mt-2">
          <TouchableOpacity className="flex-1 mr-2 bg-profit rounded-xl py-4 items-center">
            <FontAwesome name="play" size={18} color="white" />
            <Text className="text-white font-semibold mt-1">Iniciar</Text>
          </TouchableOpacity>
          <TouchableOpacity className="flex-1 ml-2 bg-dark-700 rounded-xl py-4 items-center">
            <FontAwesome name="pause" size={18} color="#94a3b8" />
            <Text className="text-dark-300 font-semibold mt-1">Pausar</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
}
