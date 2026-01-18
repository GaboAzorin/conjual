"""
Paper Trading Service

Simulates trading without using real money.
Tracks virtual balances and calculates performance metrics.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

from loguru import logger


@dataclass
class PaperTrade:
    """Record of a simulated trade."""

    id: str
    timestamp: datetime
    side: str  # "buy" or "sell"
    amount_btc: Decimal
    price_clp: Decimal
    amount_clp: Decimal
    fee_clp: Decimal
    balance_clp_after: Decimal
    balance_btc_after: Decimal


@dataclass
class PaperPortfolio:
    """Paper trading portfolio state."""

    balance_clp: Decimal = Decimal("20000")  # Starting with ~20 USD in CLP
    balance_btc: Decimal = Decimal("0")
    total_invested_clp: Decimal = Decimal("0")
    total_btc_bought: Decimal = Decimal("0")
    avg_buy_price: Decimal = Decimal("0")
    trades: list[PaperTrade] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "balance_clp": float(self.balance_clp),
            "balance_btc": float(self.balance_btc),
            "total_invested_clp": float(self.total_invested_clp),
            "total_btc_bought": float(self.total_btc_bought),
            "avg_buy_price": float(self.avg_buy_price),
            "total_trades": len(self.trades),
            "created_at": self.created_at.isoformat(),
        }


class PaperTradingService:
    """
    Simulates trading operations for paper trading mode.

    Features:
    - Virtual CLP and BTC balances
    - Realistic fee simulation (Buda: 0.8%)
    - Average buy price tracking
    - Trade history
    - Performance metrics
    """

    def __init__(
        self,
        initial_balance_clp: Decimal = Decimal("20000"),
        fee_pct: Decimal = Decimal("0.008"),
    ):
        """
        Initialize paper trading service.

        Args:
            initial_balance_clp: Starting CLP balance (default: 20000 ~ $20 USD)
            fee_pct: Trading fee percentage (default: 0.8% for Buda)
        """
        self.fee_pct = fee_pct
        self.portfolio = PaperPortfolio(balance_clp=initial_balance_clp)
        self._trade_counter = 0

        logger.info(
            f"Paper trading initialized with {initial_balance_clp} CLP, "
            f"fee: {fee_pct * 100}%"
        )

    def get_portfolio(self) -> dict:
        """
        Get current portfolio state.

        Returns:
            Dict with balance_clp, balance_btc, avg_buy_price, etc.
        """
        return self.portfolio.to_dict()

    def execute_buy(
        self,
        amount_clp: Decimal,
        price_clp: Decimal,
    ) -> Optional[PaperTrade]:
        """
        Execute a simulated buy order.

        Args:
            amount_clp: Amount of CLP to spend
            price_clp: Current BTC price in CLP

        Returns:
            PaperTrade record if successful, None otherwise
        """
        # Validate
        if amount_clp <= 0:
            logger.warning("Buy amount must be positive")
            return None

        if amount_clp > self.portfolio.balance_clp:
            logger.warning(
                f"Insufficient balance: {self.portfolio.balance_clp} CLP < {amount_clp} CLP"
            )
            return None

        # Calculate fee and BTC amount
        fee_clp = amount_clp * self.fee_pct
        net_amount_clp = amount_clp - fee_clp
        btc_bought = net_amount_clp / price_clp

        # Update balances
        self.portfolio.balance_clp -= amount_clp
        self.portfolio.balance_btc += btc_bought

        # Update average buy price (weighted average)
        old_total = self.portfolio.total_btc_bought * self.portfolio.avg_buy_price
        new_total = btc_bought * price_clp
        self.portfolio.total_btc_bought += btc_bought
        self.portfolio.total_invested_clp += amount_clp

        if self.portfolio.total_btc_bought > 0:
            self.portfolio.avg_buy_price = (
                (old_total + new_total) / self.portfolio.total_btc_bought
            )

        # Record trade
        self._trade_counter += 1
        trade = PaperTrade(
            id=f"paper_{self._trade_counter}",
            timestamp=datetime.utcnow(),
            side="buy",
            amount_btc=btc_bought,
            price_clp=price_clp,
            amount_clp=amount_clp,
            fee_clp=fee_clp,
            balance_clp_after=self.portfolio.balance_clp,
            balance_btc_after=self.portfolio.balance_btc,
        )
        self.portfolio.trades.append(trade)

        logger.success(
            f"[PAPER] BUY: {amount_clp:.0f} CLP → {btc_bought:.8f} BTC "
            f"@ {price_clp:.0f} CLP/BTC (fee: {fee_clp:.0f} CLP)"
        )

        return trade

    def execute_sell(
        self,
        amount_btc: Decimal,
        price_clp: Decimal,
    ) -> Optional[PaperTrade]:
        """
        Execute a simulated sell order.

        Args:
            amount_btc: Amount of BTC to sell
            price_clp: Current BTC price in CLP

        Returns:
            PaperTrade record if successful, None otherwise
        """
        # Validate
        if amount_btc <= 0:
            logger.warning("Sell amount must be positive")
            return None

        if amount_btc > self.portfolio.balance_btc:
            logger.warning(
                f"Insufficient BTC: {self.portfolio.balance_btc:.8f} < {amount_btc:.8f}"
            )
            return None

        # Calculate CLP and fee
        gross_clp = amount_btc * price_clp
        fee_clp = gross_clp * self.fee_pct
        net_clp = gross_clp - fee_clp

        # Update balances
        self.portfolio.balance_btc -= amount_btc
        self.portfolio.balance_clp += net_clp

        # Record trade
        self._trade_counter += 1
        trade = PaperTrade(
            id=f"paper_{self._trade_counter}",
            timestamp=datetime.utcnow(),
            side="sell",
            amount_btc=amount_btc,
            price_clp=price_clp,
            amount_clp=net_clp,
            fee_clp=fee_clp,
            balance_clp_after=self.portfolio.balance_clp,
            balance_btc_after=self.portfolio.balance_btc,
        )
        self.portfolio.trades.append(trade)

        logger.success(
            f"[PAPER] SELL: {amount_btc:.8f} BTC → {net_clp:.0f} CLP "
            f"@ {price_clp:.0f} CLP/BTC (fee: {fee_clp:.0f} CLP)"
        )

        return trade

    def calculate_performance(self, current_price: Decimal) -> dict:
        """
        Calculate performance metrics.

        Args:
            current_price: Current BTC price in CLP

        Returns:
            Dict with performance metrics
        """
        # Current portfolio value
        btc_value_clp = self.portfolio.balance_btc * current_price
        total_value_clp = self.portfolio.balance_clp + btc_value_clp

        # Initial value (what we started with)
        initial_value = self.portfolio.created_at  # We'd need to track this
        # For now, calculate based on invested amount
        if self.portfolio.total_invested_clp > 0:
            # P&L on BTC holdings
            current_btc_value = self.portfolio.balance_btc * current_price
            cost_basis = self.portfolio.balance_btc * self.portfolio.avg_buy_price
            unrealized_pnl = current_btc_value - cost_basis
            unrealized_pnl_pct = (
                (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else Decimal(0)
            )
        else:
            unrealized_pnl = Decimal(0)
            unrealized_pnl_pct = Decimal(0)

        # Total fees paid
        total_fees = sum(t.fee_clp for t in self.portfolio.trades)

        return {
            "balance_clp": float(self.portfolio.balance_clp),
            "balance_btc": float(self.portfolio.balance_btc),
            "btc_value_clp": float(btc_value_clp),
            "total_value_clp": float(total_value_clp),
            "avg_buy_price": float(self.portfolio.avg_buy_price),
            "current_price": float(current_price),
            "unrealized_pnl_clp": float(unrealized_pnl),
            "unrealized_pnl_pct": float(unrealized_pnl_pct),
            "total_fees_paid": float(total_fees),
            "total_trades": len(self.portfolio.trades),
            "total_invested_clp": float(self.portfolio.total_invested_clp),
        }

    def get_trade_history(self, limit: int = 10) -> list[dict]:
        """
        Get recent trade history.

        Args:
            limit: Maximum number of trades to return

        Returns:
            List of trade records
        """
        recent_trades = self.portfolio.trades[-limit:]

        return [
            {
                "id": t.id,
                "timestamp": t.timestamp.isoformat(),
                "side": t.side,
                "amount_btc": float(t.amount_btc),
                "price_clp": float(t.price_clp),
                "amount_clp": float(t.amount_clp),
                "fee_clp": float(t.fee_clp),
            }
            for t in reversed(recent_trades)
        ]

    def reset(self, initial_balance_clp: Decimal = Decimal("20000")):
        """Reset paper trading to initial state."""
        self.portfolio = PaperPortfolio(balance_clp=initial_balance_clp)
        self._trade_counter = 0
        logger.info(f"Paper trading reset with {initial_balance_clp} CLP")
