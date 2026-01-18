"""
Core Trading Engine
Orchestrates strategies, risk management, and order execution.
"""

import asyncio
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from loguru import logger

from app.core.config import settings
from app.services.exchange import ExchangeService
from trading.engine.paper_trading import PaperTradingService
from trading.indicators.technical import calculate_rsi, prepare_ohlcv_dataframe
from trading.risk.manager import RiskManager
from trading.strategies.base import Signal
from trading.strategies.dca import SmartDCAStrategy


class EngineState(str, Enum):
    """Trading engine states."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


class TradingEngine:
    """
    Main trading engine that orchestrates all trading operations.

    Responsibilities:
    - Manage engine lifecycle (start, stop, pause, resume)
    - Coordinate between strategies and risk manager
    - Execute trades through the exchange service
    - Log all decisions for audit trail
    """

    def __init__(self):
        self.state = EngineState.STOPPED
        self.current_strategy: Optional[str] = None
        self.paper_trading = True
        self._task: Optional[asyncio.Task] = None
        self._should_run = False

        # Components (initialized on start)
        self._exchange: Optional[ExchangeService] = None
        self._paper_service: Optional[PaperTradingService] = None
        self._risk_manager: Optional[RiskManager] = None
        self._strategy: Optional[SmartDCAStrategy] = None

        # Configuration
        self.symbol = "BTC-CLP"
        self.timeframe = "1h"
        self.loop_interval_seconds = 60  # Check every minute

        # Statistics
        self.stats = {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "total_profit_clp": 0,
            "start_time": None,
            "last_action": None,
            "last_action_time": None,
            "last_rsi": None,
            "last_price": None,
            "last_signal": None,
            "last_signal_reason": None,
            "loop_count": 0,
            "errors": 0,
        }

    @property
    def is_running(self) -> bool:
        return self.state == EngineState.RUNNING

    async def start(self, strategy: str = "smart_dca", paper_trading: bool = True) -> bool:
        """
        Start the trading engine.

        Args:
            strategy: Strategy ID to use
            paper_trading: Whether to use paper trading mode

        Returns:
            True if started successfully
        """
        if self.state not in [EngineState.STOPPED, EngineState.ERROR]:
            logger.warning(f"Cannot start engine in state: {self.state}")
            return False

        # Safety checks
        if not paper_trading and not settings.TRADING_ENABLED:
            logger.error("Real trading is disabled in settings!")
            return False

        self.state = EngineState.STARTING
        self.current_strategy = strategy
        self.paper_trading = paper_trading
        self._should_run = True

        logger.info(
            f"Starting trading engine - Strategy: {strategy}, "
            f"Paper Trading: {paper_trading}"
        )

        # Initialize components
        try:
            await self._initialize_components()
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            self.state = EngineState.ERROR
            return False

        # Start the main loop
        self._task = asyncio.create_task(self._main_loop())
        self.state = EngineState.RUNNING
        self.stats["start_time"] = datetime.utcnow().isoformat()

        logger.success("Trading engine started")
        return True

    async def _initialize_components(self):
        """Initialize all trading components."""
        # Exchange service
        self._exchange = ExchangeService(
            exchange_id="buda",
            api_key=settings.BUDA_API_KEY,
            api_secret=settings.BUDA_API_SECRET,
        )

        # Risk manager
        self._risk_manager = RiskManager(
            max_trade_pct=settings.MAX_SINGLE_TRADE_PCT,
            min_balance_clp=settings.MIN_BALANCE_CLP,
            cooldown_minutes=getattr(settings, 'TRADE_COOLDOWN_MINUTES', 30),
            max_daily_trades=getattr(settings, 'MAX_DAILY_TRADES', 3),
            fee_pct=getattr(settings, 'BUDA_FEE_PCT', 0.008),
        )

        # Paper trading service
        if self.paper_trading:
            initial_balance = Decimal(str(getattr(settings, 'PAPER_INITIAL_BALANCE_CLP', 20000)))
            self._paper_service = PaperTradingService(
                initial_balance_clp=initial_balance,
                fee_pct=Decimal(str(getattr(settings, 'BUDA_FEE_PCT', 0.008))),
            )

        # Strategy
        if self.current_strategy == "smart_dca":
            self._strategy = SmartDCAStrategy()
        else:
            raise ValueError(f"Unknown strategy: {self.current_strategy}")

        logger.info("All components initialized")

    async def stop(self) -> bool:
        """Stop the trading engine gracefully."""
        if self.state == EngineState.STOPPED:
            return True

        self.state = EngineState.STOPPING
        self._should_run = False

        # Wait for the task to complete
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        # Close exchange connection
        if self._exchange:
            await self._exchange.close()

        self.state = EngineState.STOPPED
        logger.info("Trading engine stopped")
        return True

    async def pause(self) -> bool:
        """Pause trading (keeps monitoring but doesn't execute)."""
        if self.state != EngineState.RUNNING:
            return False

        self.state = EngineState.PAUSED
        logger.info("Trading engine paused")
        return True

    async def resume(self) -> bool:
        """Resume a paused engine."""
        if self.state != EngineState.PAUSED:
            return False

        self.state = EngineState.RUNNING
        logger.info("Trading engine resumed")
        return True

    async def _main_loop(self):
        """
        Main trading loop.

        Flow:
        1. Check if paused
        2. Fetch OHLCV data
        3. Calculate RSI
        4. Get portfolio (paper or real)
        5. Call strategy.analyze()
        6. If BUY signal, validate with RiskManager
        7. Execute trade if approved
        8. Update stats and sleep
        """
        logger.info("Trading loop started")

        while self._should_run:
            try:
                self.stats["loop_count"] += 1

                # Skip if paused
                if self.state == EngineState.PAUSED:
                    self.stats["last_action"] = "paused"
                    await asyncio.sleep(5)
                    continue

                # 1. Fetch OHLCV data
                logger.debug(f"Fetching OHLCV for {self.symbol}")
                ohlcv_data = await self._exchange.get_ohlcv(
                    symbol=self.symbol,
                    timeframe=self.timeframe,
                    limit=100,
                )

                if not ohlcv_data:
                    logger.warning("No OHLCV data received")
                    self.stats["last_action"] = "no_data"
                    await asyncio.sleep(self.loop_interval_seconds)
                    continue

                # 2. Prepare DataFrame and calculate indicators
                ohlcv_df = prepare_ohlcv_dataframe(ohlcv_data)
                rsi = calculate_rsi(ohlcv_df)
                current_price = Decimal(str(ohlcv_df["close"].iloc[-1]))

                self.stats["last_rsi"] = rsi
                self.stats["last_price"] = float(current_price)

                rsi_str = f"{rsi:.1f}" if rsi is not None else "N/A"
                logger.info(
                    f"[Loop {self.stats['loop_count']}] "
                    f"Price: {current_price:.0f} CLP, RSI: {rsi_str}"
                )

                # 3. Get portfolio
                if self.paper_trading:
                    portfolio = self._paper_service.get_portfolio()
                else:
                    # Real trading - get from exchange
                    balances = await self._exchange.get_balances()
                    portfolio = self._build_portfolio_from_balances(balances)

                # 4. Call strategy
                indicators = {"rsi": rsi} if rsi is not None else {}
                signal = self._strategy.analyze(ohlcv_df, portfolio, indicators)

                self.stats["last_signal"] = signal.signal.value
                self.stats["last_signal_reason"] = signal.reason
                self.stats["last_action_time"] = datetime.utcnow().isoformat()

                logger.info(
                    f"Strategy signal: {signal.signal.value.upper()} "
                    f"(confidence: {signal.confidence:.0%}) - {signal.reason}"
                )

                # 5. Process signal
                if signal.signal == Signal.BUY:
                    await self._process_buy_signal(signal, portfolio, current_price)
                elif signal.signal == Signal.SELL:
                    await self._process_sell_signal(signal, portfolio, current_price)
                else:
                    self.stats["last_action"] = "hold"

                # Wait before next iteration
                await asyncio.sleep(self.loop_interval_seconds)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                self.stats["errors"] += 1
                self.stats["last_action"] = f"error: {str(e)[:50]}"

                # Don't change state to ERROR for transient failures
                if self.stats["errors"] > 10:
                    self.state = EngineState.ERROR
                    break

                await asyncio.sleep(30)  # Wait before retrying

        logger.info("Trading loop ended")

    async def _process_buy_signal(
        self,
        signal,
        portfolio: dict,
        current_price: Decimal,
    ):
        """Process a BUY signal."""
        balance_clp = Decimal(str(portfolio.get("balance_clp", 0)))

        # Calculate trade amount
        amount_pct = signal.suggested_amount_pct
        amount_clp = balance_clp * Decimal(str(amount_pct))

        logger.info(
            f"BUY signal: {amount_pct:.0%} of {balance_clp:.0f} CLP = {amount_clp:.0f} CLP"
        )

        # Validate with risk manager
        validation = self._risk_manager.validate_buy(
            amount_clp=amount_clp,
            balance_clp=balance_clp,
            current_price=current_price,
        )

        if not validation.approved:
            logger.warning(f"Trade REJECTED by risk manager: {validation.reason}")
            self.stats["last_action"] = f"rejected: {validation.reason[:30]}"
            return

        # Execute trade
        if self.paper_trading:
            trade = self._paper_service.execute_buy(amount_clp, current_price)
            if trade:
                self._risk_manager.record_trade()
                self._strategy.record_buy()
                self.stats["total_trades"] += 1
                self.stats["last_action"] = f"bought {trade.amount_btc:.8f} BTC"
                logger.success(
                    f"Paper trade executed: {amount_clp:.0f} CLP → "
                    f"{trade.amount_btc:.8f} BTC"
                )
        else:
            # Real trading
            try:
                # Convert CLP amount to BTC
                btc_amount = amount_clp / current_price
                order = await self._exchange.create_order(
                    symbol=self.symbol,
                    side="buy",
                    order_type="market",
                    amount=btc_amount,
                )
                self._risk_manager.record_trade()
                self._strategy.record_buy()
                self.stats["total_trades"] += 1
                self.stats["last_action"] = f"bought {order['amount']} BTC"
                logger.success(f"Real trade executed: {order}")
            except Exception as e:
                logger.error(f"Failed to execute real trade: {e}")
                self.stats["last_action"] = f"trade_error: {str(e)[:30]}"

    async def _process_sell_signal(
        self,
        signal,
        portfolio: dict,
        current_price: Decimal,
    ):
        """Process a SELL signal."""
        balance_btc = Decimal(str(portfolio.get("balance_btc", 0)))

        if balance_btc <= 0:
            logger.info("No BTC to sell")
            self.stats["last_action"] = "no_btc_to_sell"
            return

        # Calculate sell amount
        amount_pct = signal.suggested_amount_pct
        amount_btc = balance_btc * Decimal(str(amount_pct))

        avg_buy_price = Decimal(str(portfolio.get("avg_buy_price", current_price)))

        # Validate with risk manager
        validation = self._risk_manager.validate_sell(
            amount_btc=amount_btc,
            balance_btc=balance_btc,
            current_price=current_price,
            avg_buy_price=avg_buy_price,
        )

        if not validation.approved:
            logger.warning(f"Sell REJECTED: {validation.reason}")
            self.stats["last_action"] = f"sell_rejected: {validation.reason[:30]}"
            return

        # Execute trade
        if self.paper_trading:
            trade = self._paper_service.execute_sell(amount_btc, current_price)
            if trade:
                self._risk_manager.record_trade()
                self.stats["total_trades"] += 1

                # Calculate profit
                cost_basis = amount_btc * avg_buy_price
                sell_value = trade.amount_clp
                profit = sell_value - cost_basis

                if profit > 0:
                    self.stats["wins"] += 1
                else:
                    self.stats["losses"] += 1

                self.stats["total_profit_clp"] += float(profit)
                self.stats["last_action"] = f"sold {amount_btc:.8f} BTC"
        else:
            # Real trading
            try:
                order = await self._exchange.create_order(
                    symbol=self.symbol,
                    side="sell",
                    order_type="market",
                    amount=amount_btc,
                )
                self._risk_manager.record_trade()
                self.stats["total_trades"] += 1
                self.stats["last_action"] = f"sold {order['amount']} BTC"
                logger.success(f"Real sell executed: {order}")
            except Exception as e:
                logger.error(f"Failed to execute sell: {e}")
                self.stats["last_action"] = f"sell_error: {str(e)[:30]}"

    def _build_portfolio_from_balances(self, balances: list[dict]) -> dict:
        """Build portfolio dict from exchange balances."""
        portfolio = {
            "balance_clp": 0,
            "balance_btc": 0,
            "avg_buy_price": 0,  # Would need to track this separately
        }

        for balance in balances:
            if balance["currency"] == "CLP":
                portfolio["balance_clp"] = float(balance["total"])
            elif balance["currency"] == "BTC":
                portfolio["balance_btc"] = float(balance["total"])

        return portfolio

    def get_status(self) -> dict:
        """Get current engine status."""
        win_rate = (
            self.stats["wins"] / self.stats["total_trades"]
            if self.stats["total_trades"] > 0
            else 0.0
        )

        status = {
            "state": self.state.value,
            "strategy": self.current_strategy,
            "paper_trading": self.paper_trading,
            "total_trades": self.stats["total_trades"],
            "wins": self.stats["wins"],
            "losses": self.stats["losses"],
            "win_rate": round(win_rate * 100, 2),
            "total_profit_clp": self.stats["total_profit_clp"],
            "start_time": self.stats["start_time"],
            "last_action": self.stats["last_action"],
            "last_action_time": self.stats["last_action_time"],
            "last_rsi": self.stats["last_rsi"],
            "last_price": self.stats["last_price"],
            "last_signal": self.stats["last_signal"],
            "last_signal_reason": self.stats["last_signal_reason"],
            "loop_count": self.stats["loop_count"],
            "errors": self.stats["errors"],
        }

        # Add paper trading portfolio if available
        if self.paper_trading and self._paper_service:
            status["paper_portfolio"] = self._paper_service.get_portfolio()

        # Add risk manager status if available
        if self._risk_manager:
            status["risk_status"] = self._risk_manager.get_status()

        return status


# Singleton instance
_engine: Optional[TradingEngine] = None


def get_engine() -> TradingEngine:
    """Get the trading engine singleton."""
    global _engine
    if _engine is None:
        _engine = TradingEngine()
    return _engine
