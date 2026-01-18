"""
Risk Manager - Validates trades before execution.

This module ensures trades comply with risk management rules:
- Maximum trade size limits
- Cooldown between trades
- Daily trade limits
- Minimum balance requirements
- Fee impact validation
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from loguru import logger

from app.core.config import settings


@dataclass
class RiskValidation:
    """Result of a risk validation check."""

    approved: bool
    reason: str
    max_allowed_amount: Optional[Decimal] = None


class RiskManager:
    """
    Manages trading risk by validating trades against risk rules.

    Rules:
    - Maximum single trade: 20% of available balance
    - Minimum balance to maintain: 5000 CLP
    - Cooldown between trades: 30 minutes
    - Maximum daily trades: 3
    - Fee threshold: Don't trade if fees > 2% of trade
    """

    def __init__(
        self,
        max_trade_pct: float = 0.20,
        min_balance_clp: int = 5000,
        cooldown_minutes: int = 30,
        max_daily_trades: int = 3,
        fee_pct: float = 0.008,  # Buda fee: 0.8%
    ):
        self.max_trade_pct = max_trade_pct
        self.min_balance_clp = Decimal(str(min_balance_clp))
        self.cooldown_minutes = cooldown_minutes
        self.max_daily_trades = max_daily_trades
        self.fee_pct = Decimal(str(fee_pct))

        # Track trades for cooldown and daily limits
        self.last_trade_time: Optional[datetime] = None
        self.daily_trades: list[datetime] = []

    def validate_buy(
        self,
        amount_clp: Decimal,
        balance_clp: Decimal,
        current_price: Decimal,
    ) -> RiskValidation:
        """
        Validate a buy order against risk rules.

        Args:
            amount_clp: Amount to spend in CLP
            balance_clp: Current CLP balance
            current_price: Current BTC price in CLP

        Returns:
            RiskValidation with approval status and reason
        """
        # Clean up old daily trades
        self._cleanup_daily_trades()

        # Rule 1: Check daily trade limit
        if len(self.daily_trades) >= self.max_daily_trades:
            return RiskValidation(
                approved=False,
                reason=f"Límite diario alcanzado ({self.max_daily_trades} trades). "
                       f"Próximo reset en {self._time_until_reset()}."
            )

        # Rule 2: Check cooldown
        if self.last_trade_time:
            elapsed = datetime.utcnow() - self.last_trade_time
            if elapsed < timedelta(minutes=self.cooldown_minutes):
                remaining = timedelta(minutes=self.cooldown_minutes) - elapsed
                return RiskValidation(
                    approved=False,
                    reason=f"Cooldown activo. Esperar {int(remaining.total_seconds() / 60)} minutos."
                )

        # Rule 3: Check minimum balance
        remaining_balance = balance_clp - amount_clp
        if remaining_balance < self.min_balance_clp:
            max_allowed = balance_clp - self.min_balance_clp
            if max_allowed <= 0:
                return RiskValidation(
                    approved=False,
                    reason=f"Balance insuficiente. Mínimo requerido: {self.min_balance_clp} CLP."
                )
            return RiskValidation(
                approved=False,
                reason=f"Trade excede límite. Máximo permitido: {max_allowed} CLP "
                       f"(debe mantener {self.min_balance_clp} CLP).",
                max_allowed_amount=max_allowed,
            )

        # Rule 4: Check max trade percentage
        max_trade_amount = balance_clp * Decimal(str(self.max_trade_pct))
        if amount_clp > max_trade_amount:
            return RiskValidation(
                approved=False,
                reason=f"Trade excede {self.max_trade_pct * 100}% del balance. "
                       f"Máximo: {max_trade_amount:.0f} CLP.",
                max_allowed_amount=max_trade_amount,
            )

        # Rule 5: Check fee impact
        fee_amount = amount_clp * self.fee_pct
        fee_impact_pct = fee_amount / amount_clp if amount_clp > 0 else Decimal(0)

        # For very small trades, fees can be destructive
        if amount_clp < Decimal("10000"):  # Less than 10k CLP
            if fee_impact_pct > Decimal("0.02"):  # More than 2% in fees
                return RiskValidation(
                    approved=False,
                    reason=f"Trade muy pequeño. Fee ({fee_amount:.0f} CLP = {fee_impact_pct * 100:.1f}%) "
                           f"destruiría ganancias potenciales. Mínimo sugerido: 10,000 CLP."
                )

        # All checks passed
        btc_amount = (amount_clp - fee_amount) / current_price
        logger.info(
            f"Risk check APPROVED: {amount_clp:.0f} CLP → ~{btc_amount:.8f} BTC "
            f"(fee: {fee_amount:.0f} CLP)"
        )

        return RiskValidation(
            approved=True,
            reason=f"Trade aprobado. Fee estimado: {fee_amount:.0f} CLP ({self.fee_pct * 100}%)."
        )

    def validate_sell(
        self,
        amount_btc: Decimal,
        balance_btc: Decimal,
        current_price: Decimal,
        avg_buy_price: Decimal,
    ) -> RiskValidation:
        """
        Validate a sell order against risk rules.

        The DCA strategy generally doesn't sell, but this is here for completeness.

        Args:
            amount_btc: Amount of BTC to sell
            balance_btc: Current BTC balance
            current_price: Current BTC price in CLP
            avg_buy_price: Average purchase price

        Returns:
            RiskValidation with approval status and reason
        """
        # Clean up old daily trades
        self._cleanup_daily_trades()

        # Rule 1: Check daily trade limit
        if len(self.daily_trades) >= self.max_daily_trades:
            return RiskValidation(
                approved=False,
                reason=f"Límite diario alcanzado ({self.max_daily_trades} trades)."
            )

        # Rule 2: Check cooldown
        if self.last_trade_time:
            elapsed = datetime.utcnow() - self.last_trade_time
            if elapsed < timedelta(minutes=self.cooldown_minutes):
                remaining = timedelta(minutes=self.cooldown_minutes) - elapsed
                return RiskValidation(
                    approved=False,
                    reason=f"Cooldown activo. Esperar {int(remaining.total_seconds() / 60)} minutos."
                )

        # Rule 3: Check sufficient BTC balance
        if amount_btc > balance_btc:
            return RiskValidation(
                approved=False,
                reason=f"BTC insuficiente. Disponible: {balance_btc:.8f} BTC.",
                max_allowed_amount=balance_btc,
            )

        # Rule 4: Check if selling at loss (DCA strategy should HODL)
        if current_price < avg_buy_price:
            loss_pct = (avg_buy_price - current_price) / avg_buy_price * 100
            return RiskValidation(
                approved=False,
                reason=f"HODL! Precio actual ({current_price:.0f}) < precio promedio "
                       f"({avg_buy_price:.0f}). Pérdida: {loss_pct:.1f}%."
            )

        # Calculate potential gain
        gain_pct = (current_price - avg_buy_price) / avg_buy_price * 100
        clp_amount = amount_btc * current_price
        fee_amount = clp_amount * self.fee_pct

        return RiskValidation(
            approved=True,
            reason=f"Venta aprobada. Ganancia: {gain_pct:.1f}%. "
                   f"Fee: {fee_amount:.0f} CLP."
        )

    def record_trade(self):
        """Record that a trade was executed."""
        now = datetime.utcnow()
        self.last_trade_time = now
        self.daily_trades.append(now)
        logger.debug(f"Trade recorded. Daily count: {len(self.daily_trades)}")

    def _cleanup_daily_trades(self):
        """Remove trades older than 24 hours from the daily counter."""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.daily_trades = [t for t in self.daily_trades if t > cutoff]

    def _time_until_reset(self) -> str:
        """Calculate time until the oldest trade falls out of the 24h window."""
        if not self.daily_trades:
            return "ahora"

        oldest = min(self.daily_trades)
        reset_time = oldest + timedelta(hours=24)
        remaining = reset_time - datetime.utcnow()

        if remaining.total_seconds() <= 0:
            return "ahora"

        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)

        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def get_status(self) -> dict:
        """Get current risk manager status."""
        self._cleanup_daily_trades()

        cooldown_remaining = 0
        if self.last_trade_time:
            elapsed = datetime.utcnow() - self.last_trade_time
            remaining = timedelta(minutes=self.cooldown_minutes) - elapsed
            if remaining.total_seconds() > 0:
                cooldown_remaining = int(remaining.total_seconds())

        return {
            "daily_trades_used": len(self.daily_trades),
            "daily_trades_limit": self.max_daily_trades,
            "cooldown_remaining_seconds": cooldown_remaining,
            "cooldown_minutes": self.cooldown_minutes,
            "max_trade_pct": self.max_trade_pct,
            "min_balance_clp": float(self.min_balance_clp),
            "fee_pct": float(self.fee_pct),
            "last_trade_time": self.last_trade_time.isoformat() if self.last_trade_time else None,
        }


# Default instance with settings from config
def get_risk_manager() -> RiskManager:
    """Get a RiskManager instance with settings from config."""
    return RiskManager(
        max_trade_pct=settings.MAX_SINGLE_TRADE_PCT,
        min_balance_clp=settings.MIN_BALANCE_CLP,
        cooldown_minutes=getattr(settings, 'TRADE_COOLDOWN_MINUTES', 30),
        max_daily_trades=getattr(settings, 'MAX_DAILY_TRADES', 3),
        fee_pct=getattr(settings, 'BUDA_FEE_PCT', 0.008),
    )
