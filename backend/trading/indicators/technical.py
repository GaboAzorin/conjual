"""
Technical Indicators Module

Provides functions for calculating technical indicators.
Uses pure pandas implementation for compatibility with all Python versions.
"""

from decimal import Decimal
from typing import Optional

import pandas as pd
from loguru import logger


def prepare_ohlcv_dataframe(ohlcv_data: list[dict]) -> pd.DataFrame:
    """
    Convert exchange OHLCV data to a pandas DataFrame suitable for technical analysis.

    Args:
        ohlcv_data: List of OHLCV dicts from exchange service
                   [{"timestamp": ..., "open": ..., "high": ..., "low": ..., "close": ..., "volume": ...}]

    Returns:
        DataFrame with columns: timestamp, open, high, low, close, volume
        Index is datetime, values are float for TA compatibility
    """
    if not ohlcv_data:
        logger.warning("Empty OHLCV data provided")
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

    # Convert to DataFrame
    df = pd.DataFrame(ohlcv_data)

    # Convert Decimal to float for compatibility
    for col in ["open", "high", "low", "close", "volume"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: float(x) if isinstance(x, Decimal) else x)

    # Convert timestamp to datetime index
    if "timestamp" in df.columns:
        df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("datetime", inplace=True)

    # Ensure columns are in the right order
    df = df[["open", "high", "low", "close", "volume"]]

    return df


def calculate_rsi(
    ohlcv: pd.DataFrame,
    length: int = 14,
) -> Optional[float]:
    """
    Calculate RSI (Relative Strength Index) using pure pandas.

    RSI = 100 - (100 / (1 + RS))
    RS = Average Gain / Average Loss

    Args:
        ohlcv: DataFrame with OHLCV data (must have 'close' column)
        length: RSI period (default: 14)

    Returns:
        Current RSI value (0-100), or None if insufficient data
    """
    if ohlcv.empty or len(ohlcv) < length + 1:
        logger.warning(f"Insufficient data for RSI calculation. Need {length + 1} candles, got {len(ohlcv)}")
        return None

    try:
        # Calculate price changes
        delta = ohlcv["close"].diff()

        # Separate gains and losses
        gains = delta.where(delta > 0, 0.0)
        losses = (-delta).where(delta < 0, 0.0)

        # Calculate average gain and loss using EMA (Wilder's smoothing)
        avg_gain = gains.ewm(alpha=1/length, min_periods=length).mean()
        avg_loss = losses.ewm(alpha=1/length, min_periods=length).mean()

        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # Get the most recent value
        rsi_value = rsi.iloc[-1]

        if pd.isna(rsi_value):
            return None

        logger.debug(f"RSI({length}) = {rsi_value:.2f}")
        return float(rsi_value)

    except Exception as e:
        logger.error(f"Error calculating RSI: {e}")
        return None


def calculate_sma(
    ohlcv: pd.DataFrame,
    length: int = 20,
) -> Optional[float]:
    """
    Calculate Simple Moving Average.

    Args:
        ohlcv: DataFrame with OHLCV data
        length: MA period

    Returns:
        Current SMA value, or None
    """
    if ohlcv.empty or len(ohlcv) < length:
        return None

    try:
        sma = ohlcv["close"].rolling(window=length).mean()
        value = sma.iloc[-1]
        return float(value) if not pd.isna(value) else None

    except Exception as e:
        logger.error(f"Error calculating SMA: {e}")
        return None


def calculate_ema(
    ohlcv: pd.DataFrame,
    length: int = 20,
) -> Optional[float]:
    """
    Calculate Exponential Moving Average.

    Args:
        ohlcv: DataFrame with OHLCV data
        length: EMA period

    Returns:
        Current EMA value, or None
    """
    if ohlcv.empty or len(ohlcv) < length:
        return None

    try:
        ema = ohlcv["close"].ewm(span=length, adjust=False).mean()
        value = ema.iloc[-1]
        return float(value) if not pd.isna(value) else None

    except Exception as e:
        logger.error(f"Error calculating EMA: {e}")
        return None


def calculate_macd(
    ohlcv: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> Optional[dict]:
    """
    Calculate MACD (Moving Average Convergence Divergence).

    Args:
        ohlcv: DataFrame with OHLCV data
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line period (default: 9)

    Returns:
        Dict with macd, signal, and histogram values, or None
    """
    if ohlcv.empty or len(ohlcv) < slow + signal:
        logger.warning(f"Insufficient data for MACD. Need {slow + signal} candles.")
        return None

    try:
        # Calculate EMAs
        ema_fast = ohlcv["close"].ewm(span=fast, adjust=False).mean()
        ema_slow = ohlcv["close"].ewm(span=slow, adjust=False).mean()

        # MACD line
        macd_line = ema_fast - ema_slow

        # Signal line
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()

        # Histogram
        histogram = macd_line - signal_line

        return {
            "macd": float(macd_line.iloc[-1]),
            "signal": float(signal_line.iloc[-1]),
            "histogram": float(histogram.iloc[-1]),
        }

    except Exception as e:
        logger.error(f"Error calculating MACD: {e}")
        return None


def calculate_bollinger_bands(
    ohlcv: pd.DataFrame,
    length: int = 20,
    std: float = 2.0,
) -> Optional[dict]:
    """
    Calculate Bollinger Bands.

    Args:
        ohlcv: DataFrame with OHLCV data
        length: MA period (default: 20)
        std: Standard deviation multiplier (default: 2.0)

    Returns:
        Dict with upper, middle, lower band values, or None
    """
    if ohlcv.empty or len(ohlcv) < length:
        return None

    try:
        # Middle band (SMA)
        middle = ohlcv["close"].rolling(window=length).mean()

        # Standard deviation
        rolling_std = ohlcv["close"].rolling(window=length).std()

        # Upper and lower bands
        upper = middle + (rolling_std * std)
        lower = middle - (rolling_std * std)

        return {
            "upper": float(upper.iloc[-1]),
            "middle": float(middle.iloc[-1]),
            "lower": float(lower.iloc[-1]),
        }

    except Exception as e:
        logger.error(f"Error calculating Bollinger Bands: {e}")
        return None


def calculate_all_indicators(ohlcv: pd.DataFrame) -> dict:
    """
    Calculate all commonly used indicators at once.

    Args:
        ohlcv: DataFrame with OHLCV data

    Returns:
        Dict with all indicator values
    """
    indicators = {
        "rsi": calculate_rsi(ohlcv),
        "macd": calculate_macd(ohlcv),
        "bollinger": calculate_bollinger_bands(ohlcv),
        "sma_20": calculate_sma(ohlcv, 20),
        "sma_50": calculate_sma(ohlcv, 50),
        "ema_12": calculate_ema(ohlcv, 12),
        "ema_26": calculate_ema(ohlcv, 26),
    }

    # Add current price for convenience
    if not ohlcv.empty:
        indicators["current_price"] = float(ohlcv["close"].iloc[-1])

    return indicators
