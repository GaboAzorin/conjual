import { useEffect } from 'react';
import { View, Text, ScrollView, RefreshControl } from 'react-native';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { useBotStore } from '@/stores';

export default function TradesScreen() {
  const { trades, fetchTrades, isLoading, status } = useBotStore();

  useEffect(() => {
    fetchTrades();
  }, []);

  const onRefresh = async () => {
    await fetchTrades();
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

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-CL', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const stats = status?.paper_trading_stats;

  return (
    <ScrollView
      className="flex-1 bg-dark-900"
      refreshControl={
        <RefreshControl refreshing={isLoading} onRefresh={onRefresh} />
      }
    >
      <View className="p-4">
        {/* Summary Stats */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4">
          <Text className="text-white font-semibold text-lg mb-4">Resumen</Text>

          <View className="flex-row mb-4">
            <View className="flex-1 items-center">
              <Text className="text-3xl font-bold text-white">
                {stats?.total_trades || trades.length || 0}
              </Text>
              <Text className="text-dark-400 text-sm">Total Trades</Text>
            </View>
            <View className="flex-1 items-center">
              <Text className="text-3xl font-bold text-profit">
                {stats ? formatCLP(stats.profit_loss_clp) : '$0'}
              </Text>
              <Text className="text-dark-400 text-sm">P&L</Text>
            </View>
          </View>

          {stats && (
            <View className="flex-row justify-between pt-3 border-t border-dark-700">
              <View className="items-center">
                <Text className="text-white font-semibold">
                  {formatCLP(stats.avg_buy_price)}
                </Text>
                <Text className="text-dark-400 text-xs">Precio Prom.</Text>
              </View>
              <View className="items-center">
                <Text className="text-white font-semibold">
                  {formatBTC(stats.btc_balance)}
                </Text>
                <Text className="text-dark-400 text-xs">BTC Total</Text>
              </View>
              <View className="items-center">
                <Text
                  className={`font-semibold ${
                    stats.profit_loss_pct >= 0 ? 'text-profit' : 'text-loss'
                  }`}
                >
                  {stats.profit_loss_pct >= 0 ? '+' : ''}
                  {stats.profit_loss_pct.toFixed(2)}%
                </Text>
                <Text className="text-dark-400 text-xs">Rendimiento</Text>
              </View>
            </View>
          )}
        </View>

        {/* Trades List */}
        <View className="mb-4">
          <Text className="text-white font-semibold text-lg mb-3">
            Historial de Trades
          </Text>

          {trades.length === 0 ? (
            <View className="bg-dark-800 rounded-2xl p-8 items-center">
              <FontAwesome name="exchange" size={48} color="#334155" />
              <Text className="text-dark-400 mt-4 text-center">
                No hay trades aun.{'\n'}Inicia el bot para comenzar.
              </Text>
            </View>
          ) : (
            trades.map((trade, index) => (
              <View
                key={trade.id || index}
                className="bg-dark-800 rounded-xl p-4 mb-2"
              >
                <View className="flex-row items-center justify-between mb-2">
                  <View className="flex-row items-center">
                    <View
                      className={`w-8 h-8 rounded-full items-center justify-center mr-2 ${
                        trade.side === 'buy' ? 'bg-profit/20' : 'bg-loss/20'
                      }`}
                    >
                      <FontAwesome
                        name={trade.side === 'buy' ? 'arrow-down' : 'arrow-up'}
                        size={14}
                        color={trade.side === 'buy' ? '#22c55e' : '#ef4444'}
                      />
                    </View>
                    <View>
                      <Text className="text-white font-semibold">
                        {trade.side === 'buy' ? 'Compra' : 'Venta'}
                      </Text>
                      <Text className="text-dark-400 text-xs">{trade.symbol}</Text>
                    </View>
                  </View>
                  <View className="items-end">
                    <Text className="text-white font-semibold">
                      {formatBTC(trade.amount)} BTC
                    </Text>
                    <Text className="text-dark-400 text-xs">
                      @ {formatCLP(trade.price)}
                    </Text>
                  </View>
                </View>

                <View className="flex-row justify-between pt-2 border-t border-dark-700">
                  <Text className="text-dark-400 text-xs">
                    Total: {formatCLP(trade.total)}
                  </Text>
                  <Text className="text-dark-400 text-xs">
                    Fee: {formatCLP(trade.fee)}
                  </Text>
                  <Text className="text-dark-400 text-xs">
                    {formatDate(trade.executed_at || trade.created_at)}
                  </Text>
                </View>
              </View>
            ))
          )}
        </View>
      </View>
    </ScrollView>
  );
}
