"""Market data endpoints."""

from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.exchange import ExchangeService

router = APIRouter()


class TickerResponse(BaseModel):
    symbol: str
    last_price: Decimal
    bid: Decimal
    ask: Decimal
    volume_24h: Decimal
    change_24h_pct: float


class OHLCVResponse(BaseModel):
    timestamp: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


@router.get("/ticker/{symbol}", response_model=TickerResponse)
async def get_ticker(
    symbol: str,
    current_user: User = Depends(get_current_user),
):
    """Get current ticker for a symbol."""
    exchange = ExchangeService()  # Public API, no auth needed

    try:
        ticker = await exchange.get_ticker(symbol)
        return ticker
    except Exception as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=500, detail=f"Failed to fetch ticker: {str(e)}")


@router.get("/tickers")
async def get_all_tickers(
    current_user: User = Depends(get_current_user),
):
    """Get tickers for all supported pairs."""
    exchange = ExchangeService()

    try:
        tickers = await exchange.get_all_tickers()
        return {"tickers": tickers}
    except Exception as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=500, detail=f"Failed to fetch tickers: {str(e)}")


@router.get("/ohlcv/{symbol}", response_model=list[OHLCVResponse])
async def get_ohlcv(
    symbol: str,
    timeframe: str = Query("1h", regex="^(1m|5m|15m|1h|4h|1d)$"),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get OHLCV candlestick data."""
    exchange = ExchangeService()

    try:
        ohlcv = await exchange.get_ohlcv(symbol, timeframe, limit)
        return ohlcv
    except Exception as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=500, detail=f"Failed to fetch OHLCV: {str(e)}")


@router.get("/markets")
async def get_markets():
    """Get available markets (public endpoint)."""
    return {
        "markets": [
            {"symbol": "BTC-CLP", "base": "BTC", "quote": "CLP", "active": True},
            {"symbol": "ETH-CLP", "base": "ETH", "quote": "CLP", "active": True},
            {"symbol": "LTC-CLP", "base": "LTC", "quote": "CLP", "active": True},
            {"symbol": "BCH-CLP", "base": "BCH", "quote": "CLP", "active": True},
            {"symbol": "USDC-CLP", "base": "USDC", "quote": "CLP", "active": True},
        ]
    }
