#!/usr/bin/env python3
"""
Script para recolectar datos históricos de múltiples fuentes.

Uso:
    python -m scripts.collect_historical_data --days 365 --symbols BTC/USDT,ETH/USDT
    python -m scripts.collect_historical_data --buda-only --days 180

Fuentes de datos:
    1. Buda.com - Para datos BTC-CLP (mercado objetivo)
    2. Binance - Para datos BTC-USDT (más liquidez, mejor para ML)
    3. CryptoDataDownload - Para datos históricos masivos (bulk)
"""

import argparse
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import aiohttp
import ccxt.async_support as ccxt
import pandas as pd
from loguru import logger

# Configuración
DATA_DIR = Path(__file__).parent.parent / "data" / "historical"
EXCHANGES = ["binance"]  # Buda se maneja por separado
TIMEFRAMES = ["1h", "4h", "1d"]
RATE_LIMIT_DELAY = 0.5  # Segundos entre requests


async def collect_ohlcv_ccxt(
    exchange_id: str,
    symbol: str,
    timeframe: str,
    days: int,
) -> Optional[pd.DataFrame]:
    """
    Recolecta datos OHLCV de un exchange usando CCXT.

    Args:
        exchange_id: ID del exchange (binance, kraken, etc.)
        symbol: Par de trading (BTC/USDT)
        timeframe: Intervalo (1m, 5m, 15m, 1h, 4h, 1d)
        days: Días hacia atrás

    Returns:
        DataFrame con datos OHLCV o None si falla
    """
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class({"enableRateLimit": True})

    try:
        # Verificar que el exchange soporta el timeframe
        if timeframe not in exchange.timeframes:
            logger.warning(f"{exchange_id} no soporta timeframe {timeframe}")
            return None

        # Cargar mercados
        await exchange.load_markets()

        if symbol not in exchange.symbols:
            logger.warning(f"{exchange_id} no tiene el símbolo {symbol}")
            return None

        # Calcular timestamp de inicio
        since = exchange.parse8601(
            (datetime.utcnow() - timedelta(days=days)).isoformat()
        )

        all_data = []
        limit = 1000  # Máximo por request

        logger.info(f"Iniciando recolección: {exchange_id} {symbol} {timeframe}")

        while True:
            try:
                ohlcv = await exchange.fetch_ohlcv(
                    symbol, timeframe, since=since, limit=limit
                )

                if not ohlcv:
                    break

                all_data.extend(ohlcv)
                logger.debug(
                    f"{exchange_id} {symbol} {timeframe}: "
                    f"{len(ohlcv)} candles, total: {len(all_data)}"
                )

                # Actualizar since al último timestamp + 1ms
                since = ohlcv[-1][0] + 1

                # Si recibimos menos del límite, llegamos al final
                if len(ohlcv) < limit:
                    break

                await asyncio.sleep(RATE_LIMIT_DELAY)

            except ccxt.RateLimitExceeded:
                logger.warning("Rate limit exceeded, esperando 60s...")
                await asyncio.sleep(60)
                continue

            except Exception as e:
                logger.error(f"Error en fetch: {e}")
                await asyncio.sleep(5)
                break

        if not all_data:
            return None

        # Convertir a DataFrame
        df = pd.DataFrame(
            all_data,
            columns=["timestamp", "open", "high", "low", "close", "volume"],
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["exchange"] = exchange_id
        df["symbol"] = symbol
        df["timeframe"] = timeframe

        # Eliminar duplicados
        df = df.drop_duplicates(subset=["timestamp"])
        df = df.sort_values("timestamp")

        logger.success(f"Recolectados {len(df)} candles de {exchange_id} {symbol} {timeframe}")

        return df

    except Exception as e:
        logger.error(f"Error general en {exchange_id} {symbol}: {e}")
        return None

    finally:
        await exchange.close()


async def collect_buda_trades(
    symbol: str = "btc-clp",
    days: int = 365,
) -> Optional[pd.DataFrame]:
    """
    Recolecta trades históricos de Buda.com.

    Args:
        symbol: Par de trading (btc-clp, eth-clp)
        days: Días hacia atrás

    Returns:
        DataFrame con trades o None si falla
    """
    base_url = "https://www.buda.com/api/v2/markets"
    all_trades = []
    timestamp = None
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    logger.info(f"Iniciando recolección de trades Buda: {symbol}")

    async with aiohttp.ClientSession() as session:
        while True:
            params = {"limit": 100}
            if timestamp:
                params["timestamp"] = timestamp

            try:
                async with session.get(
                    f"{base_url}/{symbol}/trades",
                    params=params,
                ) as resp:
                    if resp.status != 200:
                        logger.error(f"Buda API error: {resp.status}")
                        break

                    data = await resp.json()
                    entries = data.get("trades", {}).get("entries", [])

                    if not entries:
                        break

                    all_trades.extend(entries)
                    timestamp = data["trades"]["last_timestamp"]

                    logger.debug(f"Buda {symbol}: {len(entries)} trades, total: {len(all_trades)}")

                    # Verificar si ya pasamos el límite de días
                    oldest_ts = float(entries[-1][0]) / 1000
                    oldest_date = datetime.fromtimestamp(oldest_ts)

                    if oldest_date < cutoff_date:
                        break

                    await asyncio.sleep(RATE_LIMIT_DELAY)

            except Exception as e:
                logger.error(f"Error en Buda API: {e}")
                await asyncio.sleep(5)
                continue

    if not all_trades:
        return None

    # Convertir a DataFrame
    df = pd.DataFrame(all_trades, columns=["timestamp", "amount", "price", "side"])
    df["timestamp"] = pd.to_datetime(df["timestamp"].astype(float), unit="ms")
    df["exchange"] = "buda"
    df["symbol"] = symbol

    # Convertir tipos
    df["amount"] = pd.to_numeric(df["amount"])
    df["price"] = pd.to_numeric(df["price"])

    # Eliminar duplicados y ordenar
    df = df.drop_duplicates(subset=["timestamp", "amount", "price"])
    df = df.sort_values("timestamp")

    logger.success(f"Recolectados {len(df)} trades de Buda {symbol}")

    return df


async def download_bulk_data() -> None:
    """
    Descarga datos históricos masivos de CryptoDataDownload.
    Útil para obtener años de datos sin hacer miles de requests.
    """
    bulk_urls = {
        "binance_btc_usdt_1h": "https://www.cryptodatadownload.com/cdd/Binance_BTCUSDT_1h.csv",
        "binance_eth_usdt_1h": "https://www.cryptodatadownload.com/cdd/Binance_ETHUSDT_1h.csv",
        "binance_btc_usdt_1d": "https://www.cryptodatadownload.com/cdd/Binance_BTCUSDT_d.csv",
    }

    bulk_dir = DATA_DIR.parent / "bulk"
    bulk_dir.mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        for name, url in bulk_urls.items():
            try:
                logger.info(f"Descargando {name}...")

                async with session.get(url) as resp:
                    if resp.status != 200:
                        logger.error(f"Error descargando {name}: {resp.status}")
                        continue

                    content = await resp.text()

                # CryptoDataDownload tiene una fila extra de header
                lines = content.strip().split("\n")
                csv_content = "\n".join(lines[1:])  # Saltar primera línea

                # Guardar CSV temporalmente
                temp_csv = bulk_dir / f"{name}.csv"
                temp_csv.write_text(csv_content)

                # Leer y convertir a parquet
                df = pd.read_csv(temp_csv)
                df.columns = [c.lower().strip() for c in df.columns]

                parquet_path = bulk_dir / f"{name}.parquet"
                df.to_parquet(parquet_path, index=False)

                # Eliminar CSV temporal
                temp_csv.unlink()

                logger.success(f"Guardado {name}: {len(df)} filas -> {parquet_path}")

            except Exception as e:
                logger.error(f"Error en {name}: {e}")


async def main(
    days: int,
    symbols: list[str],
    buda_only: bool = False,
    include_bulk: bool = False,
):
    """Función principal de recolección."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Recolectar datos de Buda (mercado chileno)
    buda_symbols = ["btc-clp", "eth-clp"]
    for symbol in buda_symbols:
        try:
            df = await collect_buda_trades(symbol, days)
            if df is not None:
                filepath = DATA_DIR / f"buda_{symbol}_trades.parquet"
                df.to_parquet(filepath, index=False)
                logger.success(f"Guardado {filepath}")
        except Exception as e:
            logger.error(f"Error en Buda {symbol}: {e}")

    if buda_only:
        logger.info("Modo buda-only, terminando.")
        return

    # 2. Recolectar OHLCV de exchanges internacionales
    for exchange_id in EXCHANGES:
        for symbol in symbols:
            for timeframe in TIMEFRAMES:
                try:
                    df = await collect_ohlcv_ccxt(exchange_id, symbol, timeframe, days)

                    if df is not None:
                        filename = f"{exchange_id}_{symbol.replace('/', '_')}_{timeframe}.parquet"
                        filepath = DATA_DIR / filename
                        df.to_parquet(filepath, index=False)
                        logger.success(f"Guardado {filepath}")

                except Exception as e:
                    logger.error(f"Error en {exchange_id} {symbol} {timeframe}: {e}")

    # 3. Descargar datos bulk (opcional)
    if include_bulk:
        logger.info("Descargando datos bulk de CryptoDataDownload...")
        await download_bulk_data()

    logger.success("Recolección de datos completada!")


def verify_data():
    """Verifica la integridad de los datos recolectados."""
    logger.info("Verificando datos...")

    for filepath in DATA_DIR.glob("*.parquet"):
        try:
            df = pd.read_parquet(filepath)

            # Estadísticas básicas
            logger.info(
                f"{filepath.name}: "
                f"{len(df)} filas, "
                f"desde {df['timestamp'].min()} "
                f"hasta {df['timestamp'].max()}"
            )

            # Verificar valores nulos
            null_counts = df.isnull().sum()
            if null_counts.any():
                logger.warning(f"  Valores nulos: {null_counts[null_counts > 0].to_dict()}")

        except Exception as e:
            logger.error(f"Error verificando {filepath.name}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Recolectar datos históricos de criptomonedas"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="Días de historia a recolectar (default: 365)",
    )
    parser.add_argument(
        "--symbols",
        type=str,
        default="BTC/USDT,ETH/USDT",
        help="Símbolos separados por coma (default: BTC/USDT,ETH/USDT)",
    )
    parser.add_argument(
        "--buda-only",
        action="store_true",
        help="Solo recolectar datos de Buda.com",
    )
    parser.add_argument(
        "--include-bulk",
        action="store_true",
        help="Incluir descarga de datos bulk de CryptoDataDownload",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Solo verificar datos existentes",
    )

    args = parser.parse_args()

    if args.verify:
        verify_data()
    else:
        symbols = [s.strip() for s in args.symbols.split(",")]
        asyncio.run(main(args.days, symbols, args.buda_only, args.include_bulk))
