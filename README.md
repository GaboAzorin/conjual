# CONJUAL - Sistema de Trading Inteligente Autónomo

> **Versión:** 0.1.0 (Planificación)
> **Última actualización:** 2026-01-17
> **Capital inicial:** $20,000 CLP (~$20 USD)
> **Estado:** En planificación

---

## RESUMEN EJECUTIVO

**Conjual** es un sistema de trading automatizado, personal y privado, diseñado para:
- Tomar decisiones autónomas de compra/venta de criptomonedas
- Proteger agresivamente el capital ("defenderse con garras y dientes")
- Maximizar rendimientos con bajo capital inicial
- Ser accesible desde móvil via Internet (mobile-first)

### Nivel de Confianza Global del Plan: 0.82/1.0

**Advertencias clave:**
1. $20,000 CLP es capital extremadamente bajo para trading real
2. Las regulaciones chilenas (CMF) requieren registro para servicios comerciales
3. El uso personal/privado tiene menos restricciones regulatorias
4. No hay garantía de ganancias - el mercado cripto es volátil

---

## TABLA DE CONTENIDOS

1. [Investigación y Análisis](#1-investigación-y-análisis)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Stack Tecnológico](#3-stack-tecnológico)
4. [Recolección de Datos Históricos](#4-recolección-de-datos-históricos)
5. [Plan de Implementación por Fases](#5-plan-de-implementación-por-fases)
6. [Estrategias de Trading](#6-estrategias-de-trading)
7. [Gestión de Riesgos](#7-gestión-de-riesgos)
8. [Deployment y DevOps](#8-deployment-y-devops)
9. [Control de Calidad (QA)](#9-control-de-calidad-qa)
10. [Consideraciones Legales](#10-consideraciones-legales)
11. [Roadmap Detallado](#11-roadmap-detallado)
12. [Checklist de Progreso](#12-checklist-de-progreso)

---

## 1. INVESTIGACIÓN Y ANÁLISIS

### 1.1 Exchanges Disponibles en Chile

| Exchange | API | Monedas CLP | Fees | Confianza |
|----------|-----|-------------|------|-----------|
| **Buda.com** | REST + WebSocket | ✅ Sí | 0.3-0.8% | 0.9 |
| **Orionx** | REST | ✅ Sí | 0.2-0.5% | 0.85 |
| **Binance** | REST + WebSocket | ❌ No (USDT) | 0.1% | 0.95 |

**Decisión:** Usar **Buda.com** como exchange principal por:
- Soporte nativo de CLP
- API documentada: https://api.buda.com/
- WebSocket para datos en tiempo real
- 90%+ fondos en cold storage
- 600,000+ usuarios registrados

**Fuentes:**
- [Buda.com API Docs](https://api.buda.com/)
- [Buda Reviews 2025](https://tradersunion.com/brokers/crypto/view/buda/)

### 1.2 Análisis de Capital ($20,000 CLP)

**Realidad:**
- $20,000 CLP ≈ $20 USD (enero 2026)
- Es capital **mínimo** para trading real
- Las fees pueden consumir ganancias pequeñas

**Estrategia de supervivencia:**
1. **NO hacer trading frecuente** - Las fees destruirían el capital
2. **Enfoque en HODL inteligente** - Comprar en dips, mantener
3. **DCA (Dollar Cost Averaging)** - Pequeñas compras periódicas
4. **Paper trading primero** - Practicar sin dinero real

**Nivel de confianza:** 0.75/1.0 (el capital es muy limitado)

### 1.3 Tecnologías Evaluadas

#### Backend (Python)
| Tecnología | Propósito | Madurez | Decisión |
|------------|-----------|---------|----------|
| FastAPI | API REST + WebSocket | Alta | ✅ Usar |
| CCXT | Conexión a exchanges | Alta | ✅ Usar |
| TensorTrade-NG | RL Trading Framework | Beta | ⚠️ Evaluar |
| Stable Baselines 3 | Algoritmos RL | Alta | ✅ Usar |
| FinRL | RL para Finanzas | Media | ⚠️ Alternativa |
| pandas-ta | Indicadores técnicos | Alta | ✅ Usar |

#### Frontend (Mobile)
| Tecnología | Propósito | Madurez | Decisión |
|------------|-----------|---------|----------|
| React Native + Expo | App móvil | Alta | ✅ Usar |
| NativeWind | Estilos (Tailwind) | Alta | ✅ Usar |
| Zustand | Estado global | Alta | ✅ Usar |
| React Navigation | Navegación | Alta | ✅ Usar |

**Fuentes:**
- [TensorTrade-NG Documentation](https://tensortrade-ng.io/)
- [CCXT GitHub](https://github.com/ccxt/ccxt)
- [Stable Baselines 3](https://github.com/DLR-RM/stable-baselines3)
- [Expo 2026 Guide](https://expo.dev/)

---

## 2. ARQUITECTURA DEL SISTEMA

### 2.1 Diagrama de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────────┐
│                           CONJUAL                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────────┐ │
│  │   MÓVIL      │     │   BACKEND    │     │     EXCHANGES        │ │
│  │ (React Native)│◄───►│  (FastAPI)   │◄───►│  (Buda/Binance)      │ │
│  │              │ WS  │              │ API │                      │ │
│  └──────────────┘     └──────┬───────┘     └──────────────────────┘ │
│                              │                                       │
│                              ▼                                       │
│                    ┌──────────────────┐                             │
│                    │   TRADING ENGINE │                             │
│                    │                  │                             │
│                    │ ┌──────────────┐ │                             │
│                    │ │ Strategies   │ │                             │
│                    │ │ (RL/Rules)   │ │                             │
│                    │ └──────────────┘ │                             │
│                    │ ┌──────────────┐ │                             │
│                    │ │ Risk Manager │ │                             │
│                    │ └──────────────┘ │                             │
│                    │ ┌──────────────┐ │                             │
│                    │ │ Executor     │ │                             │
│                    │ └──────────────┘ │                             │
│                    └────────┬─────────┘                             │
│                             │                                        │
│                             ▼                                        │
│                    ┌──────────────────┐                             │
│                    │    DATABASE      │                             │
│                    │   (PostgreSQL)   │                             │
│                    └──────────────────┘                             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Componentes Principales

#### A) Frontend Móvil (React Native + Expo)
```
/mobile
├── app/                    # Expo Router (file-based routing)
│   ├── (tabs)/            # Tab navigation
│   │   ├── index.tsx      # Dashboard principal
│   │   ├── portfolio.tsx  # Estado del portafolio
│   │   ├── trades.tsx     # Historial de trades
│   │   └── settings.tsx   # Configuración
│   ├── _layout.tsx        # Layout principal
│   └── login.tsx          # Autenticación
├── components/
│   ├── charts/            # Gráficos de precios
│   ├── cards/             # Cards de información
│   └── common/            # Componentes reutilizables
├── hooks/                 # Custom hooks
├── services/              # API calls
├── stores/                # Zustand stores
└── utils/                 # Utilidades
```

#### B) Backend (FastAPI + Python)
```
/backend
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py        # Autenticación JWT
│   │   │   ├── portfolio.py   # Endpoints portafolio
│   │   │   ├── trades.py      # Endpoints trades
│   │   │   ├── market.py      # Datos de mercado
│   │   │   └── bot.py         # Control del bot
│   │   └── websocket.py       # WebSocket handler
│   ├── core/
│   │   ├── config.py          # Configuración
│   │   ├── security.py        # JWT, encriptación
│   │   └── database.py        # Conexión DB
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   ├── services/
│   │   ├── exchange.py        # Conexión exchanges
│   │   └── notifications.py   # Push notifications
│   └── main.py                # Entry point
├── trading/
│   ├── engine/
│   │   ├── core.py            # Motor principal
│   │   ├── executor.py        # Ejecutor de órdenes
│   │   └── scheduler.py       # Programador de tareas
│   ├── strategies/
│   │   ├── base.py            # Clase base estrategia
│   │   ├── dca.py             # Dollar Cost Averaging
│   │   ├── grid.py            # Grid Trading
│   │   ├── momentum.py        # Momentum trading
│   │   └── ml/
│   │       ├── rl_agent.py    # Agente RL
│   │       └── trainer.py     # Entrenador
│   ├── indicators/
│   │   ├── technical.py       # RSI, MACD, BB, etc.
│   │   └── custom.py          # Indicadores propios
│   └── risk/
│       ├── manager.py         # Gestión de riesgo
│       ├── position_sizing.py # Tamaño de posiciones
│       └── stop_loss.py       # Stop loss dinámico
├── tests/
├── alembic/                   # Migraciones DB
└── requirements.txt
```

### 2.3 Flujo de Datos

```
1. DATOS DE MERCADO
   Exchange ──WebSocket──► Backend ──► Procesamiento ──► Indicadores

2. DECISIÓN DE TRADING
   Indicadores ──► Estrategia ──► Risk Manager ──► Señal (BUY/SELL/HOLD)

3. EJECUCIÓN
   Señal ──► Validación ──► Orden ──► Exchange ──► Confirmación

4. NOTIFICACIÓN
   Confirmación ──► Backend ──WebSocket──► Móvil ──► Usuario
```

---

## 3. STACK TECNOLÓGICO

### 3.1 Backend

| Componente | Tecnología | Versión | Justificación |
|------------|------------|---------|---------------|
| Lenguaje | Python | 3.11+ | Ecosistema ML/Trading |
| Framework | FastAPI | 0.110+ | Async, WebSocket, moderno |
| ORM | SQLAlchemy | 2.0+ | Async support |
| DB | PostgreSQL | 16+ | ACID, confiable |
| Cache | Redis | 7+ | Sesiones, rate limiting |
| Exchange | CCXT | 4.0+ | 108+ exchanges |
| RL | Stable Baselines 3 | 2.3+ | PPO, DQN, A2C |
| Indicadores | pandas-ta | 0.3+ | 130+ indicadores |
| Task Queue | Celery | 5.3+ | Tareas en background |

### 3.2 Frontend

| Componente | Tecnología | Versión | Justificación |
|------------|------------|---------|---------------|
| Framework | React Native | 0.76+ | Cross-platform |
| Toolchain | Expo | 52+ | DX, OTA updates |
| Routing | Expo Router | 4+ | File-based routing |
| Estilos | NativeWind | 4+ | Tailwind para RN |
| Estado | Zustand | 5+ | Ligero, simple |
| Charts | react-native-wagmi-charts | 2+ | Gráficos financieros |
| Auth | expo-secure-store | - | Almacenamiento seguro |

### 3.3 DevOps

| Componente | Tecnología | Justificación |
|------------|------------|---------------|
| Hosting Backend | Railway | Free tier, fácil deploy |
| Hosting DB | Railway PostgreSQL | Integrado |
| CI/CD | GitHub Actions | Gratis para repos públicos |
| Monitoreo | Sentry | Free tier disponible |
| Logs | Railway Logs | Incluido |

---

## 4. RECOLECCIÓN DE DATOS HISTÓRICOS

### 4.1 Fuentes de Datos

| Fuente | Tipo | Costo | Cobertura | Confianza |
|--------|------|-------|-----------|-----------|
| **Buda.com API** | REST | Gratis | BTC-CLP desde 2015 | 0.95 |
| **CryptoDataDownload** | CSV | Gratis | 2019-presente | 0.9 |
| **CCXT** | API | Gratis | 108+ exchanges | 0.95 |
| **Kraken** | CSV | Gratis | Histórico completo | 0.9 |
| **CoinGecko** | API | Gratis (30/min) | Amplia cobertura | 0.85 |

**Estrategia de datos:**
1. **Primario:** Buda.com API para datos BTC-CLP (mercado objetivo)
2. **Secundario:** CCXT + Binance para datos BTC-USDT (más liquidez, mejor para training)
3. **Backup:** CryptoDataDownload para datos históricos masivos

### 4.2 Endpoints de Datos

#### Buda.com - Trades Históricos
```python
# Endpoint: GET /api/v2/markets/{market_id}/trades
# Ejemplo para BTC-CLP:
import requests

def fetch_buda_trades(market_id: str = "btc-clp", timestamp: int = None, limit: int = 100):
    """
    Obtiene trades históricos de Buda.com

    Args:
        market_id: Par de trading (btc-clp, eth-clp, etc.)
        timestamp: Unix timestamp para paginación hacia atrás
        limit: Máximo 100 por request

    Returns:
        dict con 'entries': [[timestamp, amount, price, direction], ...]
    """
    url = f"https://www.buda.com/api/v2/markets/{market_id}/trades"
    params = {"limit": limit}
    if timestamp:
        params["timestamp"] = timestamp

    response = requests.get(url, params=params)
    return response.json()
```

#### CCXT - OHLCV Histórico
```python
import ccxt
from datetime import datetime, timedelta

def fetch_ohlcv_historical(
    exchange_id: str = "binance",
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    days_back: int = 365
) -> list:
    """
    Obtiene datos OHLCV históricos usando CCXT.
    Soporta paginación automática para períodos largos.

    Args:
        exchange_id: ID del exchange (binance, kraken, etc.)
        symbol: Par de trading
        timeframe: 1m, 5m, 15m, 1h, 4h, 1d
        days_back: Días hacia atrás

    Returns:
        Lista de [timestamp, open, high, low, close, volume]
    """
    exchange = getattr(ccxt, exchange_id)()

    # Calcular timestamp de inicio
    since = exchange.parse8601(
        (datetime.utcnow() - timedelta(days=days_back)).isoformat()
    )

    all_ohlcv = []
    limit = 1000  # Máximo por request en Binance

    while True:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
        if not ohlcv:
            break

        all_ohlcv.extend(ohlcv)
        since = ohlcv[-1][0] + 1  # Siguiente timestamp

        # Evitar rate limiting
        import time
        time.sleep(exchange.rateLimit / 1000)

        # Si recibimos menos del límite, llegamos al final
        if len(ohlcv) < limit:
            break

    return all_ohlcv
```

### 4.3 Pipeline de Recolección Automatizada

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA COLLECTION PIPELINE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────────┐ │
│  │   SCHEDULER  │────►│  COLLECTORS  │────►│     STORAGE          │ │
│  │   (Cron)     │     │              │     │                      │ │
│  └──────────────┘     │ ┌──────────┐ │     │ ┌──────────────────┐ │ │
│                       │ │ Buda     │ │     │ │ PostgreSQL       │ │ │
│  Frecuencias:         │ │ Collector│ │     │ │ (OHLCV, Trades)  │ │ │
│  - 1min: Precios      │ └──────────┘ │     │ └──────────────────┘ │ │
│  - 1h: OHLCV          │ ┌──────────┐ │     │ ┌──────────────────┐ │ │
│  - 1d: Indicadores    │ │ Binance  │ │     │ │ Parquet Files    │ │ │
│  - 1w: Retraining     │ │ Collector│ │     │ │ (Backups)        │ │ │
│                       │ └──────────┘ │     │ └──────────────────┘ │ │
│                       │ ┌──────────┐ │     │                      │ │
│                       │ │ CoinGecko│ │     │                      │ │
│                       │ │ Collector│ │     │                      │ │
│                       │ └──────────┘ │     │                      │ │
│                       └──────────────┘     └──────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.4 Estructura de Almacenamiento

#### Tabla: `ohlcv_data`
```sql
CREATE TABLE ohlcv_data (
    id SERIAL PRIMARY KEY,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open DECIMAL(20, 8) NOT NULL,
    high DECIMAL(20, 8) NOT NULL,
    low DECIMAL(20, 8) NOT NULL,
    close DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(exchange, symbol, timeframe, timestamp)
);

-- Índices para queries rápidos
CREATE INDEX idx_ohlcv_lookup ON ohlcv_data(exchange, symbol, timeframe, timestamp DESC);
CREATE INDEX idx_ohlcv_timestamp ON ohlcv_data(timestamp DESC);
```

#### Tabla: `trades_history`
```sql
CREATE TABLE trades_history (
    id SERIAL PRIMARY KEY,
    exchange VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    amount DECIMAL(20, 8) NOT NULL,
    side VARCHAR(4) NOT NULL, -- 'buy' o 'sell'
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_trades_lookup ON trades_history(exchange, symbol, timestamp DESC);
```

### 4.5 Script de Recolección Inicial

```python
# backend/scripts/collect_historical_data.py
"""
Script para descargar datos históricos iniciales.
Ejecutar una vez antes de entrenar el modelo ML.

Uso:
    python -m scripts.collect_historical_data --days 365 --symbols BTC/USDT,ETH/USDT
"""

import asyncio
import argparse
from datetime import datetime, timedelta
from pathlib import Path

import ccxt.async_support as ccxt
import pandas as pd
from loguru import logger

# Configuración
DATA_DIR = Path("data/historical")
EXCHANGES = ["binance", "kraken"]
TIMEFRAMES = ["1h", "4h", "1d"]


async def collect_ohlcv(
    exchange_id: str,
    symbol: str,
    timeframe: str,
    days: int
) -> pd.DataFrame:
    """Recolecta datos OHLCV de un exchange."""

    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class({"enableRateLimit": True})

    try:
        since = exchange.parse8601(
            (datetime.utcnow() - timedelta(days=days)).isoformat()
        )

        all_data = []

        while True:
            try:
                ohlcv = await exchange.fetch_ohlcv(
                    symbol, timeframe, since=since, limit=1000
                )

                if not ohlcv:
                    break

                all_data.extend(ohlcv)
                logger.info(
                    f"{exchange_id} {symbol} {timeframe}: "
                    f"Fetched {len(ohlcv)} candles, total: {len(all_data)}"
                )

                since = ohlcv[-1][0] + 1

                if len(ohlcv) < 1000:
                    break

            except Exception as e:
                logger.error(f"Error fetching: {e}")
                await asyncio.sleep(5)
                continue

        # Convertir a DataFrame
        df = pd.DataFrame(
            all_data,
            columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["exchange"] = exchange_id
        df["symbol"] = symbol
        df["timeframe"] = timeframe

        return df

    finally:
        await exchange.close()


async def collect_buda_trades(symbol: str = "btc-clp", days: int = 365) -> pd.DataFrame:
    """Recolecta trades históricos de Buda.com."""
    import aiohttp

    base_url = "https://www.buda.com/api/v2/markets"
    all_trades = []
    timestamp = None

    async with aiohttp.ClientSession() as session:
        while True:
            params = {"limit": 100}
            if timestamp:
                params["timestamp"] = timestamp

            async with session.get(
                f"{base_url}/{symbol}/trades",
                params=params
            ) as resp:
                data = await resp.json()

                entries = data.get("trades", {}).get("entries", [])
                if not entries:
                    break

                all_trades.extend(entries)
                timestamp = data["trades"]["last_timestamp"]

                logger.info(f"Buda {symbol}: Fetched {len(entries)} trades, total: {len(all_trades)}")

                # Verificar si ya pasamos el límite de días
                oldest_ts = int(entries[-1][0]) / 1000
                oldest_date = datetime.fromtimestamp(oldest_ts)
                if oldest_date < datetime.utcnow() - timedelta(days=days):
                    break

                await asyncio.sleep(0.5)  # Rate limiting

    # Convertir a DataFrame
    df = pd.DataFrame(all_trades, columns=["timestamp", "amount", "price", "side"])
    df["timestamp"] = pd.to_datetime(df["timestamp"].astype(float), unit="ms")
    df["exchange"] = "buda"
    df["symbol"] = symbol

    return df


async def main(days: int, symbols: list[str]):
    """Función principal de recolección."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Recolectar OHLCV de exchanges internacionales
    for exchange_id in EXCHANGES:
        for symbol in symbols:
            for timeframe in TIMEFRAMES:
                try:
                    df = await collect_ohlcv(exchange_id, symbol, timeframe, days)

                    # Guardar como Parquet
                    filename = f"{exchange_id}_{symbol.replace('/', '_')}_{timeframe}.parquet"
                    filepath = DATA_DIR / filename
                    df.to_parquet(filepath, index=False)

                    logger.success(f"Saved {filepath}: {len(df)} rows")

                except Exception as e:
                    logger.error(f"Failed {exchange_id} {symbol} {timeframe}: {e}")

    # 2. Recolectar trades de Buda.com (mercado chileno)
    try:
        df_buda = await collect_buda_trades("btc-clp", days)
        filepath = DATA_DIR / "buda_btc-clp_trades.parquet"
        df_buda.to_parquet(filepath, index=False)
        logger.success(f"Saved {filepath}: {len(df_buda)} rows")
    except Exception as e:
        logger.error(f"Failed Buda collection: {e}")

    logger.success("Data collection completed!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect historical crypto data")
    parser.add_argument("--days", type=int, default=365, help="Days of history")
    parser.add_argument(
        "--symbols",
        type=str,
        default="BTC/USDT,ETH/USDT",
        help="Comma-separated symbols"
    )

    args = parser.parse_args()
    symbols = args.symbols.split(",")

    asyncio.run(main(args.days, symbols))
```

### 4.6 Automatización con Cron/Scheduler

#### Opción 1: GitHub Actions (Gratis)
```yaml
# .github/workflows/collect-data.yml
name: Collect Market Data

on:
  schedule:
    # Cada hora
    - cron: '0 * * * *'
  workflow_dispatch:

jobs:
  collect:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install ccxt pandas pyarrow aiohttp loguru

      - name: Collect hourly data
        run: python -m scripts.collect_hourly_data
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}

      - name: Upload to storage
        uses: actions/upload-artifact@v4
        with:
          name: market-data-${{ github.run_id }}
          path: data/
```

#### Opción 2: APScheduler en el Backend
```python
# backend/app/services/data_scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()

# Recolectar precios cada minuto
scheduler.add_job(
    collect_realtime_prices,
    CronTrigger(minute="*"),
    id="collect_prices",
    replace_existing=True
)

# Recolectar OHLCV cada hora
scheduler.add_job(
    collect_hourly_ohlcv,
    CronTrigger(minute=5),  # 5 minutos después de cada hora
    id="collect_ohlcv",
    replace_existing=True
)

# Calcular indicadores diarios
scheduler.add_job(
    calculate_daily_indicators,
    CronTrigger(hour=0, minute=30),  # 00:30 UTC
    id="daily_indicators",
    replace_existing=True
)

# Re-entrenar modelo semanalmente
scheduler.add_job(
    retrain_ml_model,
    CronTrigger(day_of_week="sun", hour=3),  # Domingos 3am
    id="weekly_retrain",
    replace_existing=True
)
```

### 4.7 Descarga Masiva Inicial (CryptoDataDownload)

Para obtener años de datos históricos sin hacer miles de requests:

```python
# backend/scripts/download_bulk_data.py
"""
Descarga datos masivos de CryptoDataDownload.com
Ideal para el dataset inicial de entrenamiento.
"""

import pandas as pd
from pathlib import Path

# URLs de descarga directa (sin registro)
BULK_DATA_URLS = {
    "binance_btc_usdt_1h": "https://www.cryptodatadownload.com/cdd/Binance_BTCUSDT_1h.csv",
    "binance_eth_usdt_1h": "https://www.cryptodatadownload.com/cdd/Binance_ETHUSDT_1h.csv",
    "binance_btc_usdt_1d": "https://www.cryptodatadownload.com/cdd/Binance_BTCUSDT_d.csv",
}

def download_bulk_data(output_dir: Path = Path("data/bulk")):
    """Descarga CSVs masivos de CryptoDataDownload."""

    output_dir.mkdir(parents=True, exist_ok=True)

    for name, url in BULK_DATA_URLS.items():
        try:
            # CryptoDataDownload tiene una fila de header extra
            df = pd.read_csv(url, skiprows=1)

            # Estandarizar columnas
            df.columns = [c.lower().strip() for c in df.columns]

            # Guardar como parquet (más eficiente)
            filepath = output_dir / f"{name}.parquet"
            df.to_parquet(filepath, index=False)

            print(f"Downloaded {name}: {len(df)} rows -> {filepath}")

        except Exception as e:
            print(f"Error downloading {name}: {e}")

if __name__ == "__main__":
    download_bulk_data()
```

### 4.8 Verificación de Integridad de Datos

```python
# backend/scripts/verify_data_integrity.py
"""
Verifica que los datos históricos estén completos y sin gaps.
"""

import pandas as pd
from pathlib import Path
from loguru import logger

def check_data_gaps(df: pd.DataFrame, timeframe: str) -> list:
    """Detecta gaps en los datos OHLCV."""

    expected_delta = {
        "1m": pd.Timedelta(minutes=1),
        "5m": pd.Timedelta(minutes=5),
        "15m": pd.Timedelta(minutes=15),
        "1h": pd.Timedelta(hours=1),
        "4h": pd.Timedelta(hours=4),
        "1d": pd.Timedelta(days=1),
    }

    delta = expected_delta.get(timeframe)
    if not delta:
        raise ValueError(f"Unknown timeframe: {timeframe}")

    df = df.sort_values("timestamp")
    gaps = []

    for i in range(1, len(df)):
        actual_delta = df.iloc[i]["timestamp"] - df.iloc[i-1]["timestamp"]
        if actual_delta > delta * 1.5:  # Tolerancia del 50%
            gaps.append({
                "start": df.iloc[i-1]["timestamp"],
                "end": df.iloc[i]["timestamp"],
                "missing": actual_delta / delta - 1
            })

    return gaps


def verify_all_data(data_dir: Path = Path("data/historical")):
    """Verifica todos los archivos de datos."""

    for filepath in data_dir.glob("*.parquet"):
        df = pd.read_parquet(filepath)

        # Extraer timeframe del nombre del archivo
        parts = filepath.stem.split("_")
        timeframe = parts[-1] if parts[-1] in ["1m", "5m", "15m", "1h", "4h", "1d"] else "1h"

        gaps = check_data_gaps(df, timeframe)

        if gaps:
            logger.warning(f"{filepath.name}: Found {len(gaps)} gaps")
            for gap in gaps[:5]:  # Mostrar solo los primeros 5
                logger.warning(f"  Gap: {gap['start']} -> {gap['end']} ({gap['missing']:.0f} missing)")
        else:
            logger.success(f"{filepath.name}: No gaps detected ({len(df)} rows)")


if __name__ == "__main__":
    verify_all_data()
```

### 4.9 Resumen de Datos Necesarios

| Dataset | Fuente | Timeframe | Período | Propósito |
|---------|--------|-----------|---------|-----------|
| BTC-CLP Trades | Buda.com | Tick | 1 año | Trading real |
| BTC-USDT OHLCV | Binance | 1h, 4h, 1d | 3 años | ML Training |
| ETH-USDT OHLCV | Binance | 1h, 4h, 1d | 3 años | Diversificación |
| BTC-USDT Bulk | CryptoDataDownload | 1h | 5+ años | Backtesting |

**Estimación de tamaño:**
- BTC-USDT 1h, 3 años: ~26,000 filas (~2MB parquet)
- BTC-USDT 1d, 5 años: ~1,800 filas (~200KB parquet)
- Trades Buda 1 año: ~500,000 filas (~50MB parquet)

**Total estimado:** <100MB de datos históricos

---

## 5. PLAN DE IMPLEMENTACIÓN POR FASES

### FASE 0: SETUP INICIAL (1-2 días) ✅
**Objetivo:** Preparar el entorno de desarrollo

- [x] 0.1 Configurar estructura de carpetas
- [x] 0.2 Inicializar proyecto Python (pyproject.toml / poetry)
- [ ] 0.3 Inicializar proyecto Expo
- [ ] 0.4 Configurar git hooks (pre-commit)
- [x] 0.5 Configurar linters (ruff, eslint)
- [x] 0.6 Crear .env.example para variables de entorno
- [x] 0.7 Documentar comandos de desarrollo

**Entregables:**
- Repositorio configurado
- Entornos de desarrollo funcionando
- Documentación inicial

---

### FASE 1: BACKEND CORE (3-5 días) 🔄
**Objetivo:** API funcional básica

#### 1.1 Estructura FastAPI
- [x] 1.1.1 Setup FastAPI con estructura modular
- [x] 1.1.2 Configuración de CORS
- [x] 1.1.3 Health check endpoints
- [x] 1.1.4 Manejo de errores global
- [x] 1.1.5 Logging estructurado (loguru)

#### 1.2 Base de Datos
- [x] 1.2.1 Configurar SQLite (dev) / PostgreSQL (prod)
- [x] 1.2.2 Modelos SQLAlchemy (User, Portfolio, Trade, Order, OHLCV)
- [ ] 1.2.3 Migraciones Alembic
- [ ] 1.2.4 Seeds de datos iniciales

#### 1.3 Autenticación
- [x] 1.3.1 JWT tokens (access + refresh)
- [x] 1.3.2 Endpoints login/register/refresh
- [ ] 1.3.3 Encriptación de API keys de exchanges
- [ ] 1.3.4 Rate limiting

#### 1.4 Integración con Exchange
- [x] 1.4.1 Servicio CCXT para Buda.com
- [x] 1.4.2 Obtener balance (requiere API keys)
- [x] 1.4.3 Obtener precios en tiempo real
- [x] 1.4.4 Colocar órdenes (limit, market)
- [x] 1.4.5 Cancelar órdenes
- [x] 1.4.6 Historial de órdenes

**Entregables:**
- API REST funcional
- Conexión con Buda.com verificada
- Tests unitarios básicos

---

### FASE 2: FRONTEND MÓVIL (3-5 días)
**Objetivo:** App móvil navegable y conectada

#### 2.1 Setup Expo
- [ ] 2.1.1 Crear proyecto Expo (expo-router template)
- [ ] 2.1.2 Configurar NativeWind
- [ ] 2.1.3 Configurar tema (colores, tipografía)
- [ ] 2.1.4 Setup de navegación (tabs + stack)

#### 2.2 Pantallas Base
- [ ] 2.2.1 Splash screen
- [ ] 2.2.2 Login/Register
- [ ] 2.2.3 Dashboard principal
- [ ] 2.2.4 Portfolio view
- [ ] 2.2.5 Historial de trades
- [ ] 2.2.6 Configuración

#### 2.3 Componentes UI
- [ ] 2.3.1 Header con balance
- [ ] 2.3.2 Card de precio (BTC, ETH)
- [ ] 2.3.3 Gráfico de línea simple
- [ ] 2.3.4 Lista de transacciones
- [ ] 2.3.5 Botones de acción (Buy/Sell)
- [ ] 2.3.6 Modal de confirmación
- [ ] 2.3.7 Loading states
- [ ] 2.3.8 Empty states
- [ ] 2.3.9 Error states

#### 2.4 Conexión API
- [ ] 2.4.1 Service layer (axios/fetch)
- [ ] 2.4.2 Zustand store para auth
- [ ] 2.4.3 Zustand store para portfolio
- [ ] 2.4.4 Zustand store para precios
- [ ] 2.4.5 WebSocket para precios en tiempo real

**Entregables:**
- App instalable en dispositivo
- Flujo de login funcional
- Vista de portfolio con datos reales

---

### FASE 3: TRADING ENGINE (5-7 días)
**Objetivo:** Motor de trading con estrategias básicas

#### 3.1 Core Engine
- [ ] 3.1.1 Clase TradingEngine principal
- [ ] 3.1.2 Event loop para procesar señales
- [ ] 3.1.3 Estado del engine (running, paused, stopped)
- [ ] 3.1.4 Logging de todas las decisiones

#### 3.2 Indicadores Técnicos
- [ ] 3.2.1 RSI (Relative Strength Index)
- [ ] 3.2.2 MACD (Moving Average Convergence Divergence)
- [ ] 3.2.3 Bollinger Bands
- [ ] 3.2.4 EMA (Exponential Moving Average)
- [ ] 3.2.5 Volume indicators

#### 3.3 Estrategias Básicas
- [ ] 3.3.1 Clase base Strategy
- [ ] 3.3.2 DCA Strategy (Dollar Cost Averaging)
- [ ] 3.3.3 Grid Trading Strategy
- [ ] 3.3.4 RSI Oversold/Overbought Strategy

#### 3.4 Risk Management
- [ ] 3.4.1 Position sizing (% del portfolio)
- [ ] 3.4.2 Stop-loss dinámico
- [ ] 3.4.3 Take-profit automático
- [ ] 3.4.4 Límite de pérdida diaria
- [ ] 3.4.5 Cooldown después de pérdidas

#### 3.5 Executor
- [ ] 3.5.1 Validación pre-orden
- [ ] 3.5.2 Ejecución de órdenes
- [ ] 3.5.3 Manejo de errores de exchange
- [ ] 3.5.4 Reintentos con backoff
- [ ] 3.5.5 Confirmación y registro

**Entregables:**
- Engine funcionando en modo paper trading
- Al menos 2 estrategias implementadas
- Risk manager activo

---

### FASE 4: MACHINE LEARNING (7-10 días)
**Objetivo:** Agente RL para trading

#### 4.1 Ambiente de Trading
- [ ] 4.1.1 Custom Gym Environment
- [ ] 4.1.2 Observation space (precios, indicadores)
- [ ] 4.1.3 Action space (buy, sell, hold)
- [ ] 4.1.4 Reward function (profit + risk-adjusted)

#### 4.2 Datos Históricos
- [ ] 4.2.1 Descarga de datos históricos (Buda API)
- [ ] 4.2.2 Preprocesamiento y normalización
- [ ] 4.2.3 Feature engineering
- [ ] 4.2.4 Train/validation/test split

#### 4.3 Entrenamiento
- [ ] 4.3.1 Setup Stable Baselines 3
- [ ] 4.3.2 Entrenar agente PPO
- [ ] 4.3.3 Entrenar agente DQN
- [ ] 4.3.4 Hiperparameter tuning
- [ ] 4.3.5 Evaluación y backtesting

#### 4.4 Integración
- [ ] 4.4.1 Cargar modelo entrenado
- [ ] 4.4.2 Inferencia en tiempo real
- [ ] 4.4.3 Fallback a estrategia simple si RL falla
- [ ] 4.4.4 Logging de decisiones del modelo

**Entregables:**
- Modelo RL entrenado
- Backtesting con resultados documentados
- Integración con trading engine

---

### FASE 5: TIEMPO REAL & NOTIFICACIONES (3-4 días)
**Objetivo:** Sistema reactivo en tiempo real

#### 5.1 WebSocket Backend
- [ ] 5.1.1 WebSocket manager
- [ ] 5.1.2 Broadcast de precios
- [ ] 5.1.3 Notificaciones de trades
- [ ] 5.1.4 Estado del bot en tiempo real

#### 5.2 WebSocket Frontend
- [ ] 5.2.1 Hook useWebSocket
- [ ] 5.2.2 Reconexión automática
- [ ] 5.2.3 Actualización de UI en tiempo real

#### 5.3 Push Notifications
- [ ] 5.3.1 Setup Expo Notifications
- [ ] 5.3.2 Notificación en trade ejecutado
- [ ] 5.3.3 Alerta de grandes movimientos de precio
- [ ] 5.3.4 Configuración de preferencias

**Entregables:**
- Precios actualizándose en tiempo real
- Notificaciones push funcionando
- Sin necesidad de refresh manual

---

### FASE 6: DEPLOYMENT (2-3 días)
**Objetivo:** Sistema accesible desde Internet

#### 6.1 Backend en Railway
- [ ] 6.1.1 Dockerfile para backend
- [ ] 6.1.2 railway.toml configuración
- [ ] 6.1.3 Variables de entorno en Railway
- [ ] 6.1.4 PostgreSQL en Railway
- [ ] 6.1.5 Redis en Railway (opcional)
- [ ] 6.1.6 Domain personalizado (opcional)

#### 6.2 Frontend
- [ ] 6.2.1 Build de producción
- [ ] 6.2.2 Expo EAS Build
- [ ] 6.2.3 APK para instalación directa
- [ ] 6.2.4 OTA updates configurados

#### 6.3 CI/CD
- [ ] 6.3.1 GitHub Actions para tests
- [ ] 6.3.2 Deploy automático en push a main
- [ ] 6.3.3 Notificación en Discord/Telegram de deploys

**Entregables:**
- Backend en https://conjual-api.railway.app
- APK instalable
- CI/CD funcional

---

### FASE 7: QA & HARDENING (3-5 días)
**Objetivo:** Sistema robusto y seguro

#### 7.1 Testing
- [ ] 7.1.1 Tests unitarios (>80% coverage backend)
- [ ] 7.1.2 Tests de integración
- [ ] 7.1.3 Tests e2e del flujo de trading
- [ ] 7.1.4 Load testing básico

#### 7.2 Seguridad
- [ ] 7.2.1 Auditoría de dependencias
- [ ] 7.2.2 SSL/TLS verificado
- [ ] 7.2.3 API keys encriptadas en DB
- [ ] 7.2.4 Rate limiting estricto
- [ ] 7.2.5 Input validation exhaustiva

#### 7.3 Monitoreo
- [ ] 7.3.1 Setup Sentry para errores
- [ ] 7.3.2 Métricas de trading (wins/losses)
- [ ] 7.3.3 Alertas de sistema caído
- [ ] 7.3.4 Dashboard de métricas

**Entregables:**
- Sistema probado y documentado
- Monitoreo activo
- Plan de respuesta a incidentes

---

### FASE 8: PRODUCCIÓN (Ongoing)
**Objetivo:** Sistema en vivo con dinero real

#### 8.1 Go-Live
- [ ] 8.1.1 Paper trading por 2 semanas
- [ ] 8.1.2 Revisión final de riesgos
- [ ] 8.1.3 Depositar $20,000 CLP en Buda
- [ ] 8.1.4 Activar trading real con 10% del capital
- [ ] 8.1.5 Escalar gradualmente

#### 8.2 Operación
- [ ] 8.2.1 Revisión diaria de métricas
- [ ] 8.2.2 Ajuste de parámetros según mercado
- [ ] 8.2.3 Reentrenamiento mensual de modelo ML
- [ ] 8.2.4 Backups de base de datos

---

## 6. ESTRATEGIAS DE TRADING

### 5.1 Estrategia Principal: DCA Inteligente

Dado el capital limitado ($20,000 CLP), la estrategia principal será **DCA con timing inteligente**:

```python
class SmartDCAStrategy:
    """
    Dollar Cost Averaging con optimización por indicadores.

    - Compra periódica fija (ej: cada 3 días)
    - PERO espera si RSI > 70 (sobrecompra)
    - ACELERA si RSI < 30 (sobreventa)
    - Nunca vende en pérdida (HODL)
    """

    def should_buy(self, rsi: float, price: float, avg_price: float) -> bool:
        if rsi > 70:
            return False  # Esperar, muy caro
        if rsi < 30:
            return True   # Comprar más, ganga
        return self.is_dca_day()  # Compra normal programada
```

### 5.2 Estrategia Secundaria: Grid Trading

Para períodos de lateralización:

```
Precio actual: $100
Grid levels: $90, $95, $100, $105, $110

- Orden de compra en $95
- Orden de compra en $90
- Orden de venta en $105
- Orden de venta en $110

Profit en cada "rebote" del grid
```

### 5.3 Estrategia ML: RL Agent

Para decisiones más sofisticadas cuando haya suficientes datos:

```python
# Observation space (lo que ve el agente)
observation = {
    "price_history": [...],    # Últimos N precios
    "volume_history": [...],   # Últimos N volúmenes
    "rsi": 45.2,
    "macd": 0.003,
    "bb_position": 0.65,       # Posición en Bollinger Bands
    "portfolio_btc": 0.0001,
    "portfolio_clp": 15000,
}

# Action space
actions = ["hold", "buy_10%", "buy_25%", "sell_10%", "sell_25%"]

# Reward function
reward = profit_pct - risk_penalty - fee_penalty
```

---

## 7. GESTIÓN DE RIESGOS

### 6.1 Reglas de Hierro (NUNCA violar)

```python
RISK_RULES = {
    "max_single_trade_pct": 0.25,      # Máximo 25% por trade
    "max_daily_loss_pct": 0.10,        # Stop si pierdo 10% en un día
    "min_balance_clp": 5000,           # Siempre mantener $5,000 CLP
    "max_open_orders": 3,              # Máximo 3 órdenes abiertas
    "cooldown_after_loss_hours": 24,   # 24h sin trading después de pérdida
}
```

### 6.2 Stop Loss Dinámico

```python
def calculate_stop_loss(entry_price: float, atr: float) -> float:
    """
    Stop loss basado en volatilidad (ATR).
    Mayor volatilidad = stop loss más amplio.
    """
    return entry_price - (atr * 2)
```

### 6.3 Escenarios de Emergencia

| Escenario | Acción |
|-----------|--------|
| Caída >20% en 1 hora | Pausar bot, notificar |
| API de exchange caído | Mantener posiciones, no operar |
| Error de ejecución | Cancelar todas las órdenes |
| Pérdida >50% total | Detener bot indefinidamente |

---

## 8. DEPLOYMENT Y DEVOPS

### 7.1 Dockerfile Backend

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.2 railway.toml

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### 7.3 Variables de Entorno Requeridas

```bash
# Base de datos
DATABASE_URL=postgresql://...

# JWT
JWT_SECRET_KEY=<genera-uno-seguro>
JWT_ALGORITHM=HS256

# Exchange (Buda.com)
BUDA_API_KEY=<tu-api-key>
BUDA_API_SECRET=<tu-api-secret>

# Opcional
SENTRY_DSN=<para-monitoreo>
REDIS_URL=<si-usas-redis>
```

---

## 9. CONTROL DE CALIDAD (QA)

### 8.1 Criterios de Aceptación por Fase

#### Fase 1 (Backend)
- [x] `GET /health` retorna 200 ✓
- [x] Login genera JWT válido ✓
- [ ] Balance de Buda se obtiene correctamente (requiere API keys)
- [ ] Orden de compra (paper) ejecuta sin error (requiere API keys)

#### Fase 2 (Frontend)
- [ ] App carga en <3 segundos
- [ ] Login persiste sesión
- [ ] Balance se muestra correctamente
- [ ] Pull-to-refresh funciona

#### Fase 3 (Trading Engine)
- [ ] Bot puede pausarse/resumirse
- [ ] Stop loss se ejecuta correctamente
- [ ] Logs registran todas las decisiones
- [ ] Paper trading simula correctamente

#### Fase 4 (ML)
- [ ] Modelo entrenado supera estrategia random
- [ ] Backtesting muestra profit positivo
- [ ] Inferencia toma <100ms

### 8.2 Testing Checklist

```bash
# Backend
pytest --cov=app --cov-report=html
# Coverage mínimo: 80%

# Frontend
npm test -- --coverage
# Coverage mínimo: 70%

# E2E
# Flujo: Login → Ver balance → Ejecutar trade (paper) → Verificar historial
```

---

## 10. CONSIDERACIONES LEGALES

### 9.1 Regulación en Chile (2025)

**Ley Fintech (Ley 21.521):**
- Vigente desde enero 2023
- Full enforcement desde junio 2025
- Servicios crypto deben registrarse en CMF

**Para uso personal:**
- No requiere registro CMF
- Es tu propio dinero, tu propia cuenta de exchange
- El bot es una herramienta personal

**Impuestos:**
- Ganancias de crypto tributan como ganancia de capital
- 0-40% según tramo de ingresos
- Mantener registro de todas las transacciones

### 9.2 Disclaimer

```
CONJUAL ES UNA HERRAMIENTA DE USO PERSONAL.

- No es asesoría financiera
- El trading de criptomonedas conlleva riesgos
- Puedes perder todo tu capital
- Rendimientos pasados no garantizan rendimientos futuros
- Úsalo bajo tu propia responsabilidad
```

**Fuentes:**
- [CMF - Regulación Fintech](https://www.cmfchile.cl/)
- [Crypto Regulations Chile 2025](https://coinpedia.org/cryptocurrency-regulation/crypto-regulations-in-chile-2024/)

---

## 11. ROADMAP DETALLADO

### Timeline Estimado

```
Semana 1:  [████████░░] Fase 0 + Fase 1 (Setup + Backend)
Semana 2:  [████████░░] Fase 2 (Frontend)
Semana 3:  [██████████] Fase 3 (Trading Engine)
Semana 4:  [██████████] Fase 4 (Machine Learning)
Semana 5:  [██████░░░░] Fase 5 + 6 (Realtime + Deploy)
Semana 6:  [████████░░] Fase 7 (QA + Hardening)
Semana 7+: [░░░░░░░░░░] Fase 8 (Producción)
```

### Hitos Clave

| Hito | Descripción | Target |
|------|-------------|--------|
| M1 | Backend + Buda conectado | Fin semana 1 |
| M2 | App móvil funcional | Fin semana 2 |
| M3 | Paper trading activo | Fin semana 3 |
| M4 | Modelo ML entrenado | Fin semana 4 |
| M5 | Sistema desplegado | Fin semana 5 |
| M6 | QA completo | Fin semana 6 |
| M7 | Trading real iniciado | Semana 7+ |

---

## 12. CHECKLIST DE PROGRESO

### Estado Actual (Actualizado: 2026-01-17)

```
[██████████] 100% - Fase 0: Setup Inicial ✓
[████████░░]  80% - Fase 1: Backend Core ✓ (funcional, faltan detalles)
[░░░░░░░░░░]   0% - Fase 2: Frontend Móvil
[██░░░░░░░░]  20% - Fase 3: Trading Engine (estructura creada)
[░░░░░░░░░░]   0% - Fase 4: Machine Learning
[░░░░░░░░░░]   0% - Fase 5: Tiempo Real
[░░░░░░░░░░]   0% - Fase 6: Deployment
[░░░░░░░░░░]   0% - Fase 7: QA
[░░░░░░░░░░]   0% - Fase 8: Producción
```

### Completado en Fase 0 ✓

- [x] Estructura de carpetas creada
- [x] pyproject.toml configurado
- [x] Modelos de base de datos (User, Portfolio, Trade, Order, OHLCV)
- [x] API endpoints básicos (auth, portfolio, trades, market, bot)
- [x] WebSocket handler
- [x] Exchange service con CCXT
- [x] Script de recolección de datos históricos
- [x] GitHub Actions para automatización de datos
- [x] Dockerfile y railway.toml
- [x] .gitignore y .env.example
- [x] Trading engine core y Smart DCA strategy

### Completado en Fase 1 ✓

- [x] FastAPI funcionando en http://localhost:8000
- [x] SQLite configurado para desarrollo
- [x] Autenticación JWT con Argon2id (más seguro que bcrypt)
- [x] Endpoints de auth probados (register, login, /me)
- [x] Endpoints de mercado y estrategias funcionando
- [x] Documentación Swagger en /docs
- [x] CORS configurado
- [x] Servidor probado y estable

### Pendiente para completar Fase 1

- [ ] Agregar API keys de Buda.com al .env
- [ ] Probar conexión real con exchange
- [ ] Configurar Alembic para migraciones
- [ ] Rate limiting

### Próximos Pasos

1. **Opción A:** Agregar API keys de Buda.com y probar trading real
2. **Opción B:** Iniciar Fase 2 - Frontend móvil (React Native + Expo)
3. **Opción C:** Ejecutar recolección de datos históricos

### Comandos para continuar

```bash
# Activar entorno e iniciar servidor
cd backend
.\venv\Scripts\activate   # Windows
uvicorn app.main:app --reload

# Ver documentación API
# Abrir: http://localhost:8000/docs
```

---

## ANEXOS

### A. Comandos Útiles

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd mobile
npm install
npx expo start

# Testing
pytest
npm test

# Deploy
railway up
eas build --platform android
```

### B. Enlaces de Referencia

- [Buda.com API](https://api.buda.com/)
- [CCXT Documentation](https://docs.ccxt.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Expo Documentation](https://docs.expo.dev/)
- [Stable Baselines 3](https://stable-baselines3.readthedocs.io/)
- [Railway Deployment](https://docs.railway.com/)

### C. Contacto y Soporte

Este es un proyecto personal y privado. El README sirve como único documento de referencia para continuidad entre sesiones.

---

**Última actualización del plan:** 2026-01-17
**Próxima revisión:** Al completar cada fase

---

> *"El mercado puede permanecer irracional más tiempo del que tú puedes permanecer solvente."* - John Maynard Keynes

> *"Con $20,000 CLP, la paciencia es tu mejor estrategia."* - Conjual
