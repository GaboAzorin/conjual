"""Trading bot control endpoints."""

from enum import Enum
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.v1.auth import get_current_user
from app.models.user import User

router = APIRouter()


class BotStatus(str, Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class BotStatusResponse(BaseModel):
    status: BotStatus
    strategy: Optional[str]
    paper_trading: bool
    last_action: Optional[str]
    last_action_time: Optional[str]
    total_trades: int
    win_rate: float


class BotStartRequest(BaseModel):
    strategy: str = "smart_dca"
    paper_trading: bool = True


# In-memory bot state (TODO: Move to Redis/DB for persistence)
_bot_state = {
    "status": BotStatus.STOPPED,
    "strategy": None,
    "paper_trading": True,
    "last_action": None,
    "last_action_time": None,
    "total_trades": 0,
    "wins": 0,
}


@router.get("/status", response_model=BotStatusResponse)
async def get_bot_status(
    current_user: User = Depends(get_current_user),
):
    """Get current bot status."""
    win_rate = _bot_state["wins"] / _bot_state["total_trades"] if _bot_state["total_trades"] > 0 else 0.0

    return BotStatusResponse(
        status=_bot_state["status"],
        strategy=_bot_state["strategy"],
        paper_trading=_bot_state["paper_trading"],
        last_action=_bot_state["last_action"],
        last_action_time=_bot_state["last_action_time"],
        total_trades=_bot_state["total_trades"],
        win_rate=win_rate,
    )


@router.post("/start")
async def start_bot(
    request: BotStartRequest,
    current_user: User = Depends(get_current_user),
):
    """Start the trading bot."""
    if _bot_state["status"] == BotStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Bot is already running")

    # Safety check: require paper trading mode first
    if not request.paper_trading and not current_user.trading_enabled:
        raise HTTPException(
            status_code=403,
            detail="Real trading is not enabled for your account. Use paper trading first.",
        )

    _bot_state["status"] = BotStatus.RUNNING
    _bot_state["strategy"] = request.strategy
    _bot_state["paper_trading"] = request.paper_trading

    # TODO: Actually start the trading engine

    return {
        "message": f"Bot started with strategy: {request.strategy}",
        "paper_trading": request.paper_trading,
    }


@router.post("/stop")
async def stop_bot(
    current_user: User = Depends(get_current_user),
):
    """Stop the trading bot."""
    if _bot_state["status"] == BotStatus.STOPPED:
        raise HTTPException(status_code=400, detail="Bot is already stopped")

    _bot_state["status"] = BotStatus.STOPPED

    # TODO: Gracefully stop the trading engine

    return {"message": "Bot stopped"}


@router.post("/pause")
async def pause_bot(
    current_user: User = Depends(get_current_user),
):
    """Pause the trading bot (keeps watching but doesn't trade)."""
    if _bot_state["status"] != BotStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Bot is not running")

    _bot_state["status"] = BotStatus.PAUSED

    return {"message": "Bot paused"}


@router.post("/resume")
async def resume_bot(
    current_user: User = Depends(get_current_user),
):
    """Resume a paused bot."""
    if _bot_state["status"] != BotStatus.PAUSED:
        raise HTTPException(status_code=400, detail="Bot is not paused")

    _bot_state["status"] = BotStatus.RUNNING

    return {"message": "Bot resumed"}


@router.get("/strategies")
async def get_available_strategies():
    """Get list of available trading strategies."""
    return {
        "strategies": [
            {
                "id": "smart_dca",
                "name": "Smart DCA",
                "description": "Dollar Cost Averaging con optimización por RSI",
                "risk_level": "low",
            },
            {
                "id": "grid",
                "name": "Grid Trading",
                "description": "Trading en rangos con órdenes escalonadas",
                "risk_level": "medium",
            },
            {
                "id": "momentum",
                "name": "Momentum",
                "description": "Seguir tendencias con MACD y RSI",
                "risk_level": "high",
            },
            {
                "id": "ml_agent",
                "name": "ML Agent",
                "description": "Agente de Reinforcement Learning (PPO)",
                "risk_level": "experimental",
            },
        ]
    }
