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
import csv
import os
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


def get_last_timestamp_from_csv(filepath: Path, col_index: int = 0) -> Optional[float]:
    """Obtiene el último timestamp de un CSV para reanudar."""
    if not filepath.exists():
        return None
        
    try:
        with open(filepath, 'rb') as f:
            try:  # Catch OSError in case of a one line file 
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b'\n':
                    f.seek(-2, os.SEEK_CUR)
            except OSError:
                f.seek(0)
                
            last_line = f.readline().decode().strip()
            if not last_line or "timestamp" in last_line:  # Header or empty
                return None
                
            return float(last_line.split(',')[col_index])
    except Exception as e:
        logger.warning(f"No se pudo leer último timestamp de {filepath}: {e}")
        return None


async def collect_ohlcv_ccxt(
    exchange_id: str,
    symbol: str,
    timeframe: str,
    days: int,
) -> Optional[pd.DataFrame]:
    """
    Recolecta datos OHLCV de un exchange usando CCXT con soporte de reanudación.
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

        # Archivo temporal para checkpoints
        safe_symbol = symbol.replace('/', '_')
        temp_file = DATA_DIR / f"temp_{exchange_id}_{safe_symbol}_{timeframe}.csv"
        
        # Calcular timestamp de inicio
        start_date = datetime.utcnow() - timedelta(days=days)
        since = exchange.parse8601(start_date.isoformat())
        
        # Lógica de reanudación
        last_ts = get_last_timestamp_from_csv(temp_file, 0)
        if last_ts:
            logger.info(f"Reanudando {exchange_id} {symbol} desde {datetime.fromtimestamp(last_ts/1000)}")
            since = int(last_ts) + 1
        else:
            # Crear archivo con header si no existe
            with open(temp_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "open", "high", "low", "close", "volume"])

        limit = 1000  # Máximo por request
        total_collected = 0

        logger.info(f"Iniciando recolección: {exchange_id} {symbol} {timeframe}")

        while True:
            try:
                ohlcv = await exchange.fetch_ohlcv(
                    symbol, timeframe, since=since, limit=limit
                )

                if not ohlcv:
                    break

                # Guardar checkpoint (append)
                with open(temp_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(ohlcv)

                total_collected += len(ohlcv)
                logger.debug(
                    f"{exchange_id} {symbol} {timeframe}: "
                    f"guardados {len(ohlcv)} candles, total sesión: {total_collected}"
                )

                # Actualizar since al último timestamp + 1ms
                since = ohlcv[-1][0] + 1

                # Si recibimos menos del límite, llegamos al final (o muy cerca)
                now_ts = exchange.milliseconds()
                if len(ohlcv) < limit or ohlcv[-1][0] >= now_ts - 60000: # Margen de 1 min
                    break

                await asyncio.sleep(RATE_LIMIT_DELAY)

            except ccxt.RateLimitExceeded:
                logger.warning("Rate limit exceeded, esperando 60s...")
                await asyncio.sleep(60)
                continue

            except Exception as e:
                logger.error(f"Error en fetch: {e}")
                await asyncio.sleep(5)
                # No hacemos break aquí para intentar reanudar en el siguiente loop
                # si es un error transitorio. Pero si persiste, el usuario puede parar.
                # Para seguridad, reintentamos un par de veces o esperamos.
                # Por ahora, seguimos.

        # Al finalizar, convertir CSV completo a Parquet y limpiar
        if temp_file.exists():
            df = pd.read_csv(temp_file)
            if not df.empty:
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                df["exchange"] = exchange_id
                df["symbol"] = symbol
                df["timeframe"] = timeframe
                
                # Eliminar duplicados y ordenar
                df = df.drop_duplicates(subset=["timestamp"])
                df = df.sort_values("timestamp")
                
                logger.success(f"Recolectados {len(df)} candles de {exchange_id} {symbol} {timeframe}")
                
                # Eliminar archivo temporal si se desea, o mantenerlo como backup
                # temp_file.unlink() 
                return df
                
        return None

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
    Recolecta trades históricos de Buda.com con soporte de reanudación.
    """
    base_url = "https://www.buda.com/api/v2/markets"
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Archivo temporal
    temp_file = DATA_DIR / f"temp_buda_{symbol}_trades.csv"
    
    timestamp = None
    
    # Lógica de reanudación
    # Para Buda es más complejo reanudar hacia atrás porque paginamos desde el presente hacia el pasado.
    # Si tenemos datos parciales, probablemente tenemos los más recientes.
    # Tendríamos que ver cuál fue el último timestamp (el más antiguo) guardado y seguir desde ahí.
    
    if temp_file.exists():
        # Leer la última línea para ver cuál fue el último timestamp procesado
        # Nota: Como guardamos en orden de llegada (descendente en tiempo), 
        # la última línea del CSV es el trade más antiguo recolectado.
        last_ts_val = get_last_timestamp_from_csv(temp_file, 0)
        if last_ts_val:
            timestamp = int(last_ts_val) # Buda usa timestamp en ms como cursor
            logger.info(f"Reanudando Buda {symbol} desde timestamp {timestamp}")
    else:
        # Crear header
        with open(temp_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "amount", "price", "side", "id"])

    logger.info(f"Iniciando recolección de trades Buda: {symbol}")
    total_collected = 0

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

                    # Guardar checkpoint
                    with open(temp_file, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerows(entries)

                    total_collected += len(entries)
                    timestamp = data["trades"]["last_timestamp"] # Cursor para la siguiente página

                    logger.debug(f"Buda {symbol}: guardados {len(entries)} trades, total sesión: {total_collected}")

                    # Verificar si ya pasamos el límite de días
                    oldest_ts = float(entries[-1][0]) / 1000
                    oldest_date = datetime.fromtimestamp(oldest_ts)

                    if oldest_date < cutoff_date:
                        logger.info(f"Llegamos a la fecha límite: {oldest_date}")
                        break

                    await asyncio.sleep(RATE_LIMIT_DELAY)

            except Exception as e:
                logger.error(f"Error en Buda API: {e}")
                await asyncio.sleep(5)
                continue

    # Procesar archivo final
    if temp_file.exists():
        # Leer CSV (puede ser grande, cuidado con la memoria si son millones de filas)
        # Para 2 años de trades puede ser pesado. Usaremos chunks si es necesario, 
        # pero pandas suele aguantar bien un par de GBs.
        try:
            df = pd.read_csv(temp_file)
            if not df.empty:
                df["timestamp"] = pd.to_datetime(df["timestamp"].astype(float), unit="ms")
                df["exchange"] = "buda"
                df["symbol"] = symbol
                
                # Convertir tipos
                df["amount"] = pd.to_numeric(df["amount"])
                df["price"] = pd.to_numeric(df["price"])
                
                # Eliminar duplicados y ordenar (importante porque al reanudar puede haber overlap)
                df = df.drop_duplicates(subset=["timestamp", "amount", "price"])
                df = df.sort_values("timestamp")
                
                logger.success(f"Recolectados {len(df)} trades de Buda {symbol}")
                
                # Opcional: Borrar temporal
                # temp_file.unlink()
                return df
        except Exception as e:
            logger.error(f"Error procesando CSV final: {e}")
            return None

    return None


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
