"""
Core Trading Engine
Orchestrates strategies, risk management, and order execution.
"""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Optional

from loguru import logger

from app.core.config import settings


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

        # Statistics
        self.stats = {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "total_profit_clp": 0,
            "start_time": None,
            "last_action": None,
            "last_action_time": None,
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

        # Start the main loop
        self._task = asyncio.create_task(self._main_loop())
        self.state = EngineState.RUNNING
        self.stats["start_time"] = datetime.utcnow().isoformat()

        logger.success("Trading engine started")
        return True

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
        """Main trading loop."""
        logger.info("Trading loop started")

        while self._should_run:
            try:
                if self.state == EngineState.PAUSED:
                    await asyncio.sleep(5)
                    continue

                # 1. Fetch current market data
                # TODO: Get prices from exchange

                # 2. Calculate indicators
                # TODO: Calculate RSI, MACD, etc.

                # 3. Get strategy signal
                # TODO: Call strategy to get BUY/SELL/HOLD signal

                # 4. Check risk rules
                # TODO: Validate against risk manager

                # 5. Execute trade if signal is valid
                # TODO: Place order

                # 6. Log the decision
                self.stats["last_action"] = "monitoring"
                self.stats["last_action_time"] = datetime.utcnow().isoformat()

                # Wait before next iteration
                await asyncio.sleep(60)  # Check every minute

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                self.state = EngineState.ERROR
                await asyncio.sleep(30)  # Wait before retrying

        logger.info("Trading loop ended")

    def get_status(self) -> dict:
        """Get current engine status."""
        win_rate = (
            self.stats["wins"] / self.stats["total_trades"]
            if self.stats["total_trades"] > 0
            else 0.0
        )

        return {
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
        }


# Singleton instance
_engine: Optional[TradingEngine] = None


def get_engine() -> TradingEngine:
    """Get the trading engine singleton."""
    global _engine
    if _engine is None:
        _engine = TradingEngine()
    return _engine
