#!/bin/bash

# Script de configuración inicial para servidor Ubuntu en AWS EC2
# Uso: ./setup_server.sh

echo "🚀 Iniciando configuración del servidor CONJUAL..."

# 1. Actualizar sistema
echo "📦 Actualizando paquetes del sistema..."
sudo apt-get update && sudo apt-get upgrade -y

# 2. Instalar dependencias básicas
echo "🛠️ Instalando herramientas básicas..."
sudo apt-get install -y ca-certificates curl gnupg git

# 3. Instalar Docker
echo "🐳 Instalando Docker..."
# Add Docker's official GPG key:
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 4. Configurar permisos de Docker
echo "👤 Configurando permisos de usuario..."
sudo usermod -aG docker ubuntu

# 5. Crear estructura de directorios
echo "📂 Creando directorios del proyecto..."
mkdir -p conjual/backend
mkdir -p conjual/data

echo "✅ Configuración completada!"
echo "⚠️  Por favor, cierra sesión y vuelve a entrar para que los cambios de grupo surtan efecto (o ejecuta 'newgrp docker')."
