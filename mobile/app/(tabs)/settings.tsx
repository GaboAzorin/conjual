import { View, Text, ScrollView, TouchableOpacity, Alert, Switch } from 'react-native';
import { useState } from 'react';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { useAuthStore } from '@/stores';
import { useColorScheme } from '@/components/useColorScheme';

export default function SettingsScreen() {
  const { user, logout } = useAuthStore();
  const colorScheme = useColorScheme();
  const [notifications, setNotifications] = useState(true);
  const [autoTrade, setAutoTrade] = useState(false);

  const handleLogout = () => {
    Alert.alert('Cerrar Sesion', 'Estas seguro de cerrar sesion?', [
      { text: 'Cancelar', style: 'cancel' },
      {
        text: 'Cerrar Sesion',
        style: 'destructive',
        onPress: logout,
      },
    ]);
  };

  const SettingRow = ({
    icon,
    title,
    subtitle,
    onPress,
    rightElement,
    danger,
  }: {
    icon: string;
    title: string;
    subtitle?: string;
    onPress?: () => void;
    rightElement?: React.ReactNode;
    danger?: boolean;
  }) => (
    <TouchableOpacity
      className="flex-row items-center py-4 border-b border-dark-700"
      onPress={onPress}
      disabled={!onPress && !rightElement}
    >
      <View
        className={`w-10 h-10 rounded-xl items-center justify-center mr-3 ${
          danger ? 'bg-loss/20' : 'bg-dark-700'
        }`}
      >
        <FontAwesome
          name={icon as React.ComponentProps<typeof FontAwesome>['name']}
          size={18}
          color={danger ? '#ef4444' : '#94a3b8'}
        />
      </View>
      <View className="flex-1">
        <Text className={`font-medium ${danger ? 'text-loss' : 'text-white'}`}>
          {title}
        </Text>
        {subtitle && <Text className="text-dark-400 text-sm">{subtitle}</Text>}
      </View>
      {rightElement || (
        <FontAwesome name="chevron-right" size={14} color="#64748b" />
      )}
    </TouchableOpacity>
  );

  return (
    <ScrollView className="flex-1 bg-dark-900">
      <View className="p-4">
        {/* User Profile */}
        <View className="bg-dark-800 rounded-2xl p-5 mb-4">
          <View className="flex-row items-center">
            <View className="w-16 h-16 bg-primary-500 rounded-full items-center justify-center mr-4">
              <Text className="text-white text-2xl font-bold">
                {user?.email?.charAt(0).toUpperCase() || 'U'}
              </Text>
            </View>
            <View className="flex-1">
              <Text className="text-white font-semibold text-lg">
                {user?.email || 'Usuario'}
              </Text>
              <Text className="text-dark-400 text-sm">Cuenta Personal</Text>
            </View>
          </View>
        </View>

        {/* Trading Settings */}
        <View className="bg-dark-800 rounded-2xl px-4 mb-4">
          <Text className="text-dark-400 text-sm font-medium pt-4 pb-2">
            TRADING
          </Text>

          <SettingRow
            icon="line-chart"
            title="Estrategia"
            subtitle="Smart DCA"
          />
          <SettingRow
            icon="shield"
            title="Gestion de Riesgo"
            subtitle="Conservador"
          />
          <SettingRow
            icon="exchange"
            title="Auto-Trading"
            subtitle="Ejecutar trades automaticamente"
            rightElement={
              <Switch
                value={autoTrade}
                onValueChange={setAutoTrade}
                trackColor={{ false: '#334155', true: '#22c55e' }}
                thumbColor={autoTrade ? '#fff' : '#94a3b8'}
              />
            }
          />
        </View>

        {/* Notifications */}
        <View className="bg-dark-800 rounded-2xl px-4 mb-4">
          <Text className="text-dark-400 text-sm font-medium pt-4 pb-2">
            NOTIFICACIONES
          </Text>

          <SettingRow
            icon="bell"
            title="Notificaciones Push"
            subtitle="Alertas de trades y precios"
            rightElement={
              <Switch
                value={notifications}
                onValueChange={setNotifications}
                trackColor={{ false: '#334155', true: '#0ea5e9' }}
                thumbColor={notifications ? '#fff' : '#94a3b8'}
              />
            }
          />
        </View>

        {/* App Info */}
        <View className="bg-dark-800 rounded-2xl px-4 mb-4">
          <Text className="text-dark-400 text-sm font-medium pt-4 pb-2">
            APLICACION
          </Text>

          <SettingRow
            icon="info-circle"
            title="Version"
            subtitle="1.0.0 (Paper Trading)"
          />
          <SettingRow
            icon="moon-o"
            title="Tema"
            subtitle={colorScheme === 'dark' ? 'Oscuro' : 'Claro'}
          />
          <SettingRow icon="question-circle" title="Ayuda y Soporte" />
          <SettingRow icon="file-text-o" title="Terminos y Condiciones" />
        </View>

        {/* Account */}
        <View className="bg-dark-800 rounded-2xl px-4 mb-4">
          <Text className="text-dark-400 text-sm font-medium pt-4 pb-2">
            CUENTA
          </Text>

          <SettingRow
            icon="key"
            title="API Keys"
            subtitle="Configurar conexion con Buda.com"
          />
          <SettingRow
            icon="sign-out"
            title="Cerrar Sesion"
            onPress={handleLogout}
            danger
          />
        </View>

        {/* Disclaimer */}
        <View className="p-4 mt-2">
          <Text className="text-dark-500 text-xs text-center">
            Conjual v1.0.0{'\n'}
            Sistema de trading personal.{'\n'}
            No es asesoria financiera.
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}
