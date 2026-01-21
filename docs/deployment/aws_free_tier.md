# Guía de Despliegue en AWS Free Tier (EC2)

Esta guía detalla cómo desplegar CONJUAL en una instancia EC2 de AWS aprovechando la capa gratuita (Free Tier).

## 1. Requisitos Previos (Lo que necesitas TÚ)

### 1.1 Cuenta AWS
- **Crear cuenta**: Ve a [aws.amazon.com](https://aws.amazon.com/es/free/) y regístrate.
- **Tarjeta de Crédito**: Te pedirán una para verificar identidad (cobran $1 USD y lo devuelven).
- **Capa Gratuita (Free Tier)**: Actualmente ofrecen **6 meses** de prueba con créditos (antes eran 12), lo cual es suficiente para validar nuestro piloto.

### 1.2 No necesito tus claves
- **Seguridad**: Yo (la IA) **NO** necesito tus credenciales de acceso a AWS.
- **Operación**: Tú crearás el servidor desde la consola web de AWS y descargarás un archivo "llave" (`.pem`) a tu computador. Yo te daré los comandos para usar esa llave.

### 1.3 Qué es el archivo .pem
- Es tu "llave física" para entrar al servidor.
- **Importante**: Cuando AWS te pregunte "Key Pair", elige "Create new key pair", ponle nombre (ej: `conjual-key`) y descarga el archivo. **Guárdalo en una carpeta segura y no lo pierdas**, AWS no guarda copia.

## 2. Lanzar Instancia EC2 (Paso a Paso)

1. **Buscar EC2**:
   - En la barra de búsqueda superior (donde dice `[Alt+S]`), escribe **"EC2"**.
   - Haz clic en la primera opción "EC2 Virtual Servers in the Cloud".

2. **Iniciar el Asistente**:
   - Busca el botón naranja que dice **"Lanzar instancia"** (Launch instance).

3. **Configuración de la Instancia**:
   - **Nombre**: Escribe `conjual-server`.
   - **Imágenes de aplicación y SO**: Selecciona **Ubuntu**.
     - Asegúrate que diga "Apto para la capa gratuita" (Free tier eligible).
   - **Tipo de instancia**: Deja la que viene por defecto (usualmente `t2.micro` o `t3.micro`).

4. **🔑 PAR DE CLAVES (Aquí obtienes el .pem)**:
   - Busca la sección **"Par de claves (inicio de sesión)"**.
   - Haz clic en el enlace azul a la derecha: **"Crear nuevo par de claves"**.
   - Se abrirá una ventanita:
     - **Nombre del par de claves**: Ponle `conjual-key`.
     - **Tipo de par de claves**: `RSA`.
     - **Formato de archivo de clave privada**: Selecciona `.pem`.
   - Haz clic en el botón naranja **"Crear par de claves"**.
   - **¡OJO!**: Se descargará automáticamente un archivo llamado `conjual-key.pem`. **Guárdalo bien**, no podrás bajarlo de nuevo.

5. **Configuraciones de Red**:
   - Marca la casilla: ✅ **"Permitir el tráfico de SSH desde"** -> **"Cualquier lugar"** (0.0.0.0/0).
   - Marca la casilla: ✅ **"Permitir el tráfico de HTTPS desde Internet"**.
   - Marca la casilla: ✅ **"Permitir el tráfico de HTTP desde Internet"**.

6. **Almacenamiento**:
   - Donde dice `8 GiB`, cámbialo a `30 GiB` (es el máximo gratis).

7. **Finalizar**:
   - Haz clic en el botón naranja a la derecha: **"Lanzar instancia"**.

## 3. Conexión al Servidor

1. **Mover la llave**: Mueve el archivo `.pem` que descargaste a la carpeta de este proyecto (`conjual`).
   - *Nota: Ya configuré `.gitignore` para que git ignore este archivo y no lo subas por error.*

2. **Obtener la dirección del servidor**:
   - En la consola de AWS, selecciona tu instancia `conjual-server` (haz clic en el cuadradito azul a la izquierda).
   - Abajo aparecerá un panel con detalles. Copia lo que dice en **"Dirección IPv4 pública"** (ej: `54.123.45.67`).

3. **Conectar vía Terminal**:
   Abre una terminal aquí en VS Code y ejecuta:

   ```powershell
   # Ajusta el nombre del archivo si es distinto
   ssh -i "conjual-key.pem" ubuntu@TU_IP_PUBLICA
   ```

   *Si te pregunta "Are you sure you want to continue connecting?", escribe `yes` y dale Enter.*

## 5. Subir el Código (Deploy)

Una vez que la instalación automática termine (cuando veas "✅ Listo!"), sigue estos pasos:

1. **Cierra la sesión actual**:
   Escribe `exit` y dale Enter en la terminal del servidor.

2. **Sube el código**:
   Desde tu terminal local (PowerShell en VS Code), ejecuta este comando para copiar la carpeta `backend` al servidor:

   ```powershell
   # Asegúrate de estar en la carpeta raíz del proyecto (donde está conjual-key.pem)
   scp -i "conjual-key.pem" -r backend ubuntu@TU_IP_PUBLICA:~/conjual/
   ```
   *(Reemplaza `TU_IP_PUBLICA` por tu IP real, ej: 3.144.95.182)*

3. **Conéctate de nuevo**:
   ```powershell
   ssh -i "conjual-key.pem" ubuntu@TU_IP_PUBLICA
   ```

4. **Lanza la aplicación**:
   Ya dentro del servidor, ejecuta:

   ```bash
   cd conjual/backend
   
   # Crea el archivo .env (copia y pega esto)
   cat << EOF > .env
   DATABASE_URL=postgresql+asyncpg://conjual:conjual_password_secure@db:5432/conjual
   ENVIRONMENT=production
   # Agrega aquí tus claves si quieres:
   # BUDA_API_KEY=tu_clave
   # BUDA_API_SECRET=tu_secreto
   EOF

   # Levanta los contenedores
   docker compose up -d --build
   ```

5. **¡Listo!**
   Verifica que esté corriendo con: `docker compose ps`



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
