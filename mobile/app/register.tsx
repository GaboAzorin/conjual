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
  ScrollView,
} from 'react-native';
import { Link } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { useAuthStore } from '@/stores';

export default function RegisterScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const { register, isLoading, error, clearError } = useAuthStore();

  const handleRegister = async () => {
    if (!email || !password || !confirmPassword) {
      Alert.alert('Error', 'Por favor completa todos los campos');
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert('Error', 'Las contrasenas no coinciden');
      return;
    }

    if (password.length < 6) {
      Alert.alert('Error', 'La contrasena debe tener al menos 6 caracteres');
      return;
    }

    clearError();
    const success = await register({ email, password });

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

      <ScrollView
        className="flex-1"
        contentContainerStyle={{ flexGrow: 1, justifyContent: 'center' }}
        keyboardShouldPersistTaps="handled"
      >
        <View className="px-8 py-12">
          {/* Header */}
          <View className="items-center mb-10">
            <View className="w-16 h-16 bg-profit rounded-2xl items-center justify-center mb-4">
              <FontAwesome name="user-plus" size={32} color="white" />
            </View>
            <Text className="text-3xl font-bold text-white">Crear Cuenta</Text>
            <Text className="text-dark-400 mt-2">Unete a Conjual</Text>
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
                  placeholder="Minimo 6 caracteres"
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

            {/* Confirm Password Input */}
            <View className="mt-4">
              <Text className="text-dark-300 mb-2 ml-1">Confirmar Contrasena</Text>
              <View className="flex-row items-center bg-dark-800 rounded-xl px-4">
                <FontAwesome name="lock" size={20} color="#64748b" />
                <TextInput
                  className="flex-1 py-4 px-3 text-white"
                  placeholder="Repite tu contrasena"
                  placeholderTextColor="#64748b"
                  value={confirmPassword}
                  onChangeText={setConfirmPassword}
                  secureTextEntry={!showPassword}
                />
              </View>
            </View>

            {/* Register Button */}
            <TouchableOpacity
              className={`mt-8 py-4 rounded-xl items-center ${
                isLoading ? 'bg-profit/70' : 'bg-profit'
              }`}
              onPress={handleRegister}
              disabled={isLoading}
            >
              {isLoading ? (
                <ActivityIndicator color="white" />
              ) : (
                <Text className="text-white font-semibold text-lg">Crear Cuenta</Text>
              )}
            </TouchableOpacity>

            {/* Login Link */}
            <View className="flex-row justify-center mt-6">
              <Text className="text-dark-400">Ya tienes cuenta? </Text>
              <Link href="/login" asChild>
                <TouchableOpacity>
                  <Text className="text-primary-400 font-semibold">Inicia Sesion</Text>
                </TouchableOpacity>
              </Link>
            </View>
          </View>

          {/* Disclaimer */}
          <View className="mt-10 p-4 bg-dark-800 rounded-xl">
            <Text className="text-dark-400 text-xs text-center">
              Al crear una cuenta aceptas que Conjual es una herramienta de uso personal
              para trading automatizado. El trading de criptomonedas conlleva riesgos.
              Puedes perder todo tu capital.
            </Text>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
