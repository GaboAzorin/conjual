"""
Base strategy class that all trading strategies must inherit from.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional

import pandas as pd


class Signal(str, Enum):
    """Trading signal types."""

    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class TradeSignal:
    """A trading signal with metadata."""

    signal: Signal
    confidence: float  # 0.0 to 1.0
    reason: str
    suggested_amount_pct: float = 0.0  # Percentage of portfolio
    suggested_price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.

    All strategies must implement the `analyze` method which takes
    market data and returns a trading signal.
    """

    name: str = "base"
    description: str = "Base strategy"
    risk_level: str = "low"  # low, medium, high, experimental

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize strategy with optional configuration.

        Args:
            config: Strategy-specific configuration parameters
        """
        self.config = config or {}

    @abstractmethod
    def analyze(
        self,
        ohlcv: pd.DataFrame,
        portfolio: dict,
        indicators: Optional[dict] = None,
    ) -> TradeSignal:
        """
        Analyze market data and return a trading signal.

        Args:
            ohlcv: DataFrame with OHLCV data (timestamp, open, high, low, close, volume)
            portfolio: Current portfolio state (balances, positions)
            indicators: Pre-calculated technical indicators (optional)

        Returns:
            TradeSignal with the recommended action
        """
        pass

    def validate_signal(self, signal: TradeSignal) -> bool:
        """
        Validate a signal before execution.
        Override in subclasses for custom validation.

        Args:
            signal: The signal to validate

        Returns:
            True if signal is valid
        """
        if signal.confidence < 0 or signal.confidence > 1:
            return False

        if signal.signal in [Signal.BUY, Signal.SELL]:
            if signal.suggested_amount_pct <= 0:
                return False

        return True

    def get_info(self) -> dict:
        """Get strategy information."""
        return {
            "name": self.name,
            "description": self.description,
            "risk_level": self.risk_level,
            "config": self.config,
        }
