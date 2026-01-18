"""Trading bot control endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.v1.auth import get_current_user
from app.core.config import settings
from app.models.user import User
from trading.engine.core import get_engine, EngineState

router = APIRouter()


class BotStatusResponse(BaseModel):
    """Bot status response model."""

    state: str
    strategy: Optional[str]
    paper_trading: bool
    total_trades: int
    wins: int
    losses: int
    win_rate: float
    total_profit_clp: float
    start_time: Optional[str]
    last_action: Optional[str]
    last_action_time: Optional[str]
    last_rsi: Optional[float]
    last_price: Optional[float]
    last_signal: Optional[str]
    last_signal_reason: Optional[str]
    loop_count: int
    errors: int
    paper_portfolio: Optional[dict] = None
    risk_status: Optional[dict] = None


class BotStartRequest(BaseModel):
    """Request to start the bot."""

    strategy: str = "smart_dca"
    paper_trading: bool = True


class BotStartResponse(BaseModel):
    """Response after starting the bot."""

    message: str
    paper_trading: bool
    strategy: str


@router.get("/status", response_model=BotStatusResponse)
async def get_bot_status(
    current_user: User = Depends(get_current_user),
):
    """
    Get current bot status.

    Returns detailed information about the trading engine including:
    - Current state (stopped, running, paused, etc.)
    - Active strategy
    - Trading statistics
    - Last action and signals
    - Paper portfolio (if in paper trading mode)
    - Risk manager status
    """
    engine = get_engine()
    status = engine.get_status()

    return BotStatusResponse(**status)


@router.post("/start", response_model=BotStartResponse)
async def start_bot(
    request: BotStartRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Start the trading bot.

    By default, starts in paper trading mode for safety.
    Real trading requires:
    - paper_trading=false in the request
    - TRADING_ENABLED=true in settings
    - User must have trading_enabled=true
    """
    engine = get_engine()

    # Check if already running
    if engine.state in [EngineState.RUNNING, EngineState.STARTING]:
        raise HTTPException(status_code=400, detail="Bot is already running")

    # Safety check: require paper trading mode unless explicitly enabled
    if not request.paper_trading:
        if not settings.TRADING_ENABLED:
            raise HTTPException(
                status_code=403,
                detail="Real trading is disabled in server settings. Set TRADING_ENABLED=true to enable.",
            )
        if not current_user.trading_enabled:
            raise HTTPException(
                status_code=403,
                detail="Real trading is not enabled for your account. Contact admin or use paper trading.",
            )

    # Start the engine
    success = await engine.start(
        strategy=request.strategy,
        paper_trading=request.paper_trading,
    )

    if not success:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start bot. Current state: {engine.state.value}",
        )

    return BotStartResponse(
        message=f"Bot started with strategy: {request.strategy}",
        paper_trading=request.paper_trading,
        strategy=request.strategy,
    )


@router.post("/stop")
async def stop_bot(
    current_user: User = Depends(get_current_user),
):
    """
    Stop the trading bot.

    Gracefully stops the trading engine and closes exchange connections.
    """
    engine = get_engine()

    if engine.state == EngineState.STOPPED:
        raise HTTPException(status_code=400, detail="Bot is already stopped")

    success = await engine.stop()

    if not success:
        raise HTTPException(status_code=500, detail="Failed to stop bot")

    return {"message": "Bot stopped", "state": engine.state.value}


@router.post("/pause")
async def pause_bot(
    current_user: User = Depends(get_current_user),
):
    """
    Pause the trading bot.

    Pauses trading activity but keeps monitoring the market.
    Use resume to continue trading.
    """
    engine = get_engine()

    if engine.state != EngineState.RUNNING:
        raise HTTPException(
            status_code=400,
            detail=f"Bot is not running. Current state: {engine.state.value}",
        )

    success = await engine.pause()

    if not success:
        raise HTTPException(status_code=500, detail="Failed to pause bot")

    return {"message": "Bot paused", "state": engine.state.value}


@router.post("/resume")
async def resume_bot(
    current_user: User = Depends(get_current_user),
):
    """
    Resume a paused bot.

    Resumes trading activity after being paused.
    """
    engine = get_engine()

    if engine.state != EngineState.PAUSED:
        raise HTTPException(
            status_code=400,
            detail=f"Bot is not paused. Current state: {engine.state.value}",
        )

    success = await engine.resume()

    if not success:
        raise HTTPException(status_code=500, detail="Failed to resume bot")

    return {"message": "Bot resumed", "state": engine.state.value}


@router.get("/strategies")
async def get_available_strategies():
    """
    Get list of available trading strategies.

    Returns all strategies that can be used with the trading bot.
    """
    return {
        "strategies": [
            {
                "id": "smart_dca",
                "name": "Smart DCA",
                "description": "Dollar Cost Averaging con optimización por RSI",
                "risk_level": "low",
                "recommended": True,
            },
            {
                "id": "grid",
                "name": "Grid Trading",
                "description": "Trading en rangos con órdenes escalonadas",
                "risk_level": "medium",
                "recommended": False,
                "available": False,  # Not yet implemented
            },
            {
                "id": "momentum",
                "name": "Momentum",
                "description": "Seguir tendencias con MACD y RSI",
                "risk_level": "high",
                "recommended": False,
                "available": False,  # Not yet implemented
            },
            {
                "id": "ml_agent",
                "name": "ML Agent",
                "description": "Agente de Reinforcement Learning (PPO)",
                "risk_level": "experimental",
                "recommended": False,
                "available": False,  # Not yet implemented
            },
        ]
    }


@router.get("/trades")
async def get_recent_trades(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
):
    """
    Get recent trades (paper trading only for now).

    Returns the trade history from the paper trading service.
    """
    engine = get_engine()

    if not engine.paper_trading or not engine._paper_service:
        return {"trades": [], "message": "No paper trading service active"}

    trades = engine._paper_service.get_trade_history(limit=limit)
    return {"trades": trades}


@router.get("/performance")
async def get_performance(
    current_user: User = Depends(get_current_user),
):
    """
    Get performance metrics.

    Returns detailed performance statistics for paper trading.
    """
    engine = get_engine()

    if not engine.paper_trading or not engine._paper_service:
        return {"error": "No paper trading service active"}

    # Get current price from status
    current_price = engine.stats.get("last_price")
    if current_price is None:
        return {"error": "No price data available. Start the bot first."}

    from decimal import Decimal
    performance = engine._paper_service.calculate_performance(
        Decimal(str(current_price))
    )

    return performance
