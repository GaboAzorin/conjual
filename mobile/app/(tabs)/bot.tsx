import { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { useBotStore } from '@/stores';

export default function BotScreen() {
  const {
    status,
    isLoading,
    fetchStatus,
    startBot,
    stopBot,
    pauseBot,
    resumeBot,
  } = useBotStore();
  const [selectedStrategy] = useState('smart_dca');

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleStart = async () => {
    Alert.alert(
      'Iniciar Bot',
      'Se iniciara el bot en modo Paper Trading (sin dinero real). Continuar?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Iniciar',
          onPress: async () => {
            const success = await startBot({
              paper_trading: true,
              strategy: selectedStrategy,
              initial_balance: 20000,
            });
            if (success) {
              Alert.alert('Exito', 'Bot iniciado correctamente');
            }
          },
        },
      ]
    );
  };

  const handleStop = async () => {
    Alert.alert('Detener Bot', 'Estas seguro de detener el bot?', [
      { text: 'Cancelar', style: 'cancel' },
      {
        text: 'Detener',
        style: 'destructive',
        onPress: async () => {
          await stopBot();
        },
      },
    ]);
  };

  const handlePause = async () => {
    await pauseBot();
  };

  const handleResume = async () => {
    await resumeBot();
  };

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${hours}h ${minutes}m ${secs}s`;
  };

  const isRunning = status?.status === 'running';
  const isPaused = status?.status === 'paused';
  const isStopped = !status || status.status === 'stopped';

  return (
    <ScrollView className="flex-1 bg-dark-900">
      <View className="p-4">
        {/* Status Header */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4">
          <View className="items-center">
            <View
              className={`w-24 h-24 rounded-full items-center justify-center mb-4 ${
                isRunning
                  ? 'bg-profit/20'
                  : isPaused
                  ? 'bg-accent/20'
                  : 'bg-dark-700'
              }`}
            >
              <FontAwesome
                name="android"
                size={48}
                color={isRunning ? '#22c55e' : isPaused ? '#f59e0b' : '#64748b'}
              />
            </View>
            <Text className="text-white text-2xl font-bold mb-2">
              {isRunning ? 'Bot Activo' : isPaused ? 'Bot Pausado' : 'Bot Detenido'}
            </Text>
            {status?.uptime_seconds !== undefined && status.uptime_seconds > 0 && (
              <Text className="text-dark-400">
                Uptime: {formatUptime(status.uptime_seconds)}
              </Text>
            )}
          </View>
        </View>

        {/* Controls */}
        <View className="mb-4">
          <Text className="text-white font-semibold text-lg mb-3">Controles</Text>

          {isStopped ? (
            <TouchableOpacity
              className="bg-profit rounded-xl py-4 items-center flex-row justify-center"
              onPress={handleStart}
              disabled={isLoading}
            >
              {isLoading ? (
                <ActivityIndicator color="white" />
              ) : (
                <>
                  <FontAwesome name="play" size={20} color="white" />
                  <Text className="text-white font-semibold text-lg ml-2">
                    Iniciar Bot
                  </Text>
                </>
              )}
            </TouchableOpacity>
          ) : (
            <View className="flex-row">
              {isPaused ? (
                <TouchableOpacity
                  className="flex-1 mr-2 bg-profit rounded-xl py-4 items-center flex-row justify-center"
                  onPress={handleResume}
                  disabled={isLoading}
                >
                  <FontAwesome name="play" size={18} color="white" />
                  <Text className="text-white font-semibold ml-2">Reanudar</Text>
                </TouchableOpacity>
              ) : (
                <TouchableOpacity
                  className="flex-1 mr-2 bg-accent rounded-xl py-4 items-center flex-row justify-center"
                  onPress={handlePause}
                  disabled={isLoading}
                >
                  <FontAwesome name="pause" size={18} color="#0f172a" />
                  <Text className="text-dark-900 font-semibold ml-2">Pausar</Text>
                </TouchableOpacity>
              )}
              <TouchableOpacity
                className="flex-1 ml-2 bg-loss rounded-xl py-4 items-center flex-row justify-center"
                onPress={handleStop}
                disabled={isLoading}
              >
                <FontAwesome name="stop" size={18} color="white" />
                <Text className="text-white font-semibold ml-2">Detener</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>

        {/* Strategy Info */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4">
          <Text className="text-white font-semibold text-lg mb-3">Estrategia</Text>

          <View className="bg-dark-700 rounded-xl p-4 border-2 border-primary-500">
            <View className="flex-row items-center mb-2">
              <FontAwesome name="line-chart" size={18} color="#0ea5e9" />
              <Text className="text-white font-semibold ml-2">Smart DCA</Text>
            </View>
            <Text className="text-dark-400 text-sm">
              Dollar Cost Averaging inteligente con RSI. Compra periodicamente pero
              evita sobrecompra (RSI &gt; 70) y acelera en sobreventa (RSI &lt; 30).
            </Text>
          </View>
        </View>

        {/* Risk Parameters */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4">
          <Text className="text-white font-semibold text-lg mb-3">
            Parametros de Riesgo
          </Text>

          <View className="space-y-3">
            <View className="flex-row justify-between py-2 border-b border-dark-700">
              <Text className="text-dark-400">Max. por trade</Text>
              <Text className="text-white">20%</Text>
            </View>
            <View className="flex-row justify-between py-2 border-b border-dark-700">
              <Text className="text-dark-400">Balance minimo</Text>
              <Text className="text-white">$5,000 CLP</Text>
            </View>
            <View className="flex-row justify-between py-2 border-b border-dark-700">
              <Text className="text-dark-400">Cooldown</Text>
              <Text className="text-white">30 min</Text>
            </View>
            <View className="flex-row justify-between py-2">
              <Text className="text-dark-400">Max. trades/dia</Text>
              <Text className="text-white">3</Text>
            </View>
          </View>
        </View>

        {/* Mode Badge */}
        <View className="bg-accent/20 rounded-xl p-4 flex-row items-center">
          <FontAwesome name="flask" size={20} color="#f59e0b" />
          <View className="ml-3">
            <Text className="text-accent font-semibold">Modo Paper Trading</Text>
            <Text className="text-dark-400 text-sm">
              Simulacion sin dinero real. Ideal para pruebas.
            </Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}
