import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { Link } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { useAuthStore } from '@/stores';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const { login, isLoading, error, clearError } = useAuthStore();

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Por favor ingresa email y contrasena');
      return;
    }

    clearError();
    const success = await login({ username: email, password });

    if (!success && error) {
      Alert.alert('Error', error);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      className="flex-1 bg-dark-900"
    >
      <StatusBar style="light" />

      <View className="flex-1 justify-center px-8">
        {/* Logo/Title */}
        <View className="items-center mb-12">
          <View className="w-20 h-20 bg-primary-500 rounded-2xl items-center justify-center mb-4">
            <FontAwesome name="bitcoin" size={48} color="white" />
          </View>
          <Text className="text-4xl font-bold text-white">Conjual</Text>
          <Text className="text-dark-400 mt-2">Trading Inteligente Autonomo</Text>
        </View>

        {/* Form */}
        <View className="space-y-4">
          {/* Email Input */}
          <View>
            <Text className="text-dark-300 mb-2 ml-1">Email</Text>
            <View className="flex-row items-center bg-dark-800 rounded-xl px-4">
              <FontAwesome name="envelope" size={18} color="#64748b" />
              <TextInput
                className="flex-1 py-4 px-3 text-white"
                placeholder="tu@email.com"
                placeholderTextColor="#64748b"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
              />
            </View>
          </View>

          {/* Password Input */}
          <View className="mt-4">
            <Text className="text-dark-300 mb-2 ml-1">Contrasena</Text>
            <View className="flex-row items-center bg-dark-800 rounded-xl px-4">
              <FontAwesome name="lock" size={20} color="#64748b" />
              <TextInput
                className="flex-1 py-4 px-3 text-white"
                placeholder="********"
                placeholderTextColor="#64748b"
                value={password}
                onChangeText={setPassword}
                secureTextEntry={!showPassword}
              />
              <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                <FontAwesome
                  name={showPassword ? 'eye-slash' : 'eye'}
                  size={18}
                  color="#64748b"
                />
              </TouchableOpacity>
            </View>
          </View>

          {/* Login Button */}
          <TouchableOpacity
            className={`mt-8 py-4 rounded-xl items-center ${
              isLoading ? 'bg-primary-700' : 'bg-primary-500'
            }`}
            onPress={handleLogin}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator color="white" />
            ) : (
              <Text className="text-white font-semibold text-lg">Iniciar Sesion</Text>
            )}
          </TouchableOpacity>

          {/* Register Link */}
          <View className="flex-row justify-center mt-6">
            <Text className="text-dark-400">No tienes cuenta? </Text>
            <Link href="/register" asChild>
              <TouchableOpacity>
                <Text className="text-primary-400 font-semibold">Registrate</Text>
              </TouchableOpacity>
            </Link>
          </View>
        </View>

        {/* Footer */}
        <View className="mt-12 items-center">
          <Text className="text-dark-500 text-xs text-center">
            Sistema de trading personal y privado.{'\n'}
            No es asesoria financiera.
          </Text>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}
