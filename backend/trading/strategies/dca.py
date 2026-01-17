"""
Smart DCA (Dollar Cost Averaging) Strategy

A conservative strategy optimized for low capital that:
- Makes periodic purchases (DCA)
- Optimizes entry points using RSI
- Never sells at a loss (HODL)
- Accelerates buying during dips
"""

from decimal import Decimal
from typing import Optional

import pandas as pd
import pandas_ta as ta

from trading.strategies.base import BaseStrategy, Signal, TradeSignal


class SmartDCAStrategy(BaseStrategy):
    """
    Smart Dollar Cost Averaging strategy with RSI optimization.

    Configuration:
        - dca_interval_hours: Hours between DCA purchases (default: 72 = 3 days)
        - rsi_overbought: RSI level considered overbought (default: 70)
        - rsi_oversold: RSI level considered oversold (default: 30)
        - base_amount_pct: Base purchase amount as % of portfolio (default: 10%)
        - accelerate_amount_pct: Extra amount when oversold (default: 15%)
    """

    name = "smart_dca"
    description = "Dollar Cost Averaging con optimización por RSI"
    risk_level = "low"

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)

        # Default configuration
        self.dca_interval_hours = self.config.get("dca_interval_hours", 72)
        self.rsi_overbought = self.config.get("rsi_overbought", 70)
        self.rsi_oversold = self.config.get("rsi_oversold", 30)
        self.base_amount_pct = self.config.get("base_amount_pct", 0.10)
        self.accelerate_amount_pct = self.config.get("accelerate_amount_pct", 0.15)

        # State
        self.last_buy_time = None

    def analyze(
        self,
        ohlcv: pd.DataFrame,
        portfolio: dict,
        indicators: Optional[dict] = None,
    ) -> TradeSignal:
        """
        Analyze market and decide whether to buy.

        DCA Logic:
        1. If RSI > 70 (overbought): HOLD - don't buy, too expensive
        2. If RSI < 30 (oversold): BUY MORE - accelerated purchase
        3. Otherwise: BUY if it's DCA day, else HOLD
        """

        # Calculate RSI if not provided
        if indicators and "rsi" in indicators:
            rsi = indicators["rsi"]
        else:
            rsi_series = ta.rsi(ohlcv["close"], length=14)
            rsi = rsi_series.iloc[-1] if not rsi_series.empty else 50

        current_price = Decimal(str(ohlcv["close"].iloc[-1]))

        # Get portfolio info
        balance_clp = Decimal(str(portfolio.get("balance_clp", 0)))
        balance_btc = Decimal(str(portfolio.get("balance_btc", 0)))
        avg_buy_price = Decimal(str(portfolio.get("avg_buy_price", current_price)))

        # Decision logic
        if rsi > self.rsi_overbought:
            # Overbought - wait for better entry
            return TradeSignal(
                signal=Signal.HOLD,
                confidence=0.8,
                reason=f"RSI={rsi:.1f} > {self.rsi_overbought} (overbought). Esperando mejor entrada.",
                suggested_amount_pct=0,
            )

        elif rsi < self.rsi_oversold:
            # Oversold - great opportunity, buy more!
            amount_pct = self.base_amount_pct + self.accelerate_amount_pct

            # Don't use more than 25% in a single trade
            amount_pct = min(amount_pct, 0.25)

            return TradeSignal(
                signal=Signal.BUY,
                confidence=0.85,
                reason=f"RSI={rsi:.1f} < {self.rsi_oversold} (sobreventa). Oportunidad de compra acelerada!",
                suggested_amount_pct=amount_pct,
                suggested_price=current_price,
            )

        else:
            # Normal DCA - check if it's time to buy
            if self._is_dca_time():
                return TradeSignal(
                    signal=Signal.BUY,
                    confidence=0.7,
                    reason=f"DCA programado. RSI={rsi:.1f} en rango normal.",
                    suggested_amount_pct=self.base_amount_pct,
                    suggested_price=current_price,
                )
            else:
                return TradeSignal(
                    signal=Signal.HOLD,
                    confidence=0.6,
                    reason=f"RSI={rsi:.1f} normal. Esperando próximo ciclo DCA.",
                    suggested_amount_pct=0,
                )

    def _is_dca_time(self) -> bool:
        """Check if it's time for a DCA purchase."""
        from datetime import datetime, timedelta

        now = datetime.utcnow()

        if self.last_buy_time is None:
            return True

        hours_since_last = (now - self.last_buy_time).total_seconds() / 3600
        return hours_since_last >= self.dca_interval_hours

    def record_buy(self):
        """Record a buy action to track DCA timing."""
        from datetime import datetime

        self.last_buy_time = datetime.utcnow()
