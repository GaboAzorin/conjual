# Guía de Despliegue en AWS Free Tier (EC2)

Esta guía detalla cómo desplegar CONJUAL en una instancia EC2 de AWS aprovechando la capa gratuita (Free Tier).

## 1. Requisitos Previos

- Cuenta de AWS activa.
- Par de claves SSH (`.pem`) creado y descargado.
- Repositorio de código accesible (GitHub/GitLab) o método para subir archivos (SCP).

## 2. Lanzar Instancia EC2

1. **Ir a EC2 Dashboard** > **Launch Instances**.
2. **Name**: `conjual-server`.
3. **OS Image**: Ubuntu Server 24.04 LTS (HVM), SSD Volume Type (Free tier eligible).
4. **Instance Type**: `t2.micro` o `t3.micro` (dependiendo de la región y disponibilidad Free Tier).
5. **Key Pair**: Selecciona tu par de claves existente.
6. **Network Settings**:
   - Create security group.
   - Allow SSH traffic from Anywhere (o tu IP).
   - Allow HTTP traffic from the internet.
   - Allow HTTPS traffic from the internet.
7. **Storage**: 30 GiB gp3 (El Free Tier permite hasta 30GB).
8. **Launch Instance**.

## 3. Configuración del Servidor

Conéctate vía SSH:
```bash
ssh -i "tu-clave.pem" ubuntu@tu-public-dns
```

### 3.1 Instalar Docker y Docker Compose

```bash
# Actualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Dar permisos al usuario ubuntu
sudo usermod -aG docker ubuntu

# Activar cambios de grupo (o reiniciar sesión)
newgrp docker

# Verificar instalación
docker --version
docker compose version
```

## 4. Despliegue de la Aplicación

### 4.1 Clonar Repositorio

```bash
git clone https://github.com/tu-usuario/conjual.git
cd conjual
```

### 4.2 Configurar Variables de Entorno

Crear archivo `.env` en la raíz (basado en `.env.example`):

```bash
cp .env.example .env
nano .env
```

**Variables Críticas:**
- `DATABASE_URL`: `postgresql+asyncpg://postgres:password@db:5432/conjual` (si usas docker-compose con DB) o la URL de tu RDS.
- `BUDA_API_KEY`: Tu API Key.
- `BUDA_API_SECRET`: Tu Secret.

### 4.3 Iniciar Servicios

```bash
# Construir y levantar contenedores en segundo plano
docker compose up -d --build
```

### 4.4 Verificar Estado

```bash
docker compose ps
docker compose logs -f backend
```

## 5. Mantenimiento y Logs

- **Ver logs en tiempo real**: `docker compose logs -f`
- **Reiniciar servicios**: `docker compose restart`
- **Actualizar código**:
  ```bash
  git pull
  docker compose up -d --build
  ```

## 6. Consideraciones de Costo

- **EC2**: 750 horas/mes gratis el primer año (suficiente para 1 instancia 24/7).
- **EBS**: 30GB gratis.
- **Data Transfer**: 100GB/mes de salida gratis.

**¡IMPORTANTE!**: Configura alertas de facturación (Billing Alarms) en AWS para evitar sorpresas.
