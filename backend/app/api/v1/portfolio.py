"""Portfolio endpoints."""

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.exchange import ExchangeService

router = APIRouter()


class BalanceResponse(BaseModel):
    currency: str
    available: Decimal
    frozen: Decimal
    total: Decimal


class PortfolioResponse(BaseModel):
    balances: list[BalanceResponse]
    total_value_clp: Decimal
    exchange: str


@router.get("/balance", response_model=PortfolioResponse)
async def get_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current portfolio balance from exchange."""
    if not current_user.buda_api_key or not current_user.buda_api_secret:
        raise HTTPException(
            status_code=400,
            detail="Exchange API keys not configured. Please add your Buda.com API keys.",
        )

    exchange = ExchangeService(
        api_key=current_user.buda_api_key,
        api_secret=current_user.buda_api_secret,
    )

    try:
        balances = await exchange.get_balances()
        total_value = await exchange.calculate_total_value_clp(balances)

        return PortfolioResponse(
            balances=balances,
            total_value_clp=total_value,
            exchange="buda",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch balance: {str(e)}")


@router.get("/summary")
async def get_portfolio_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get portfolio summary with P&L."""
    # TODO: Implement portfolio summary with historical data
    return {
        "total_value_clp": 20000,
        "initial_value_clp": 20000,
        "pnl_clp": 0,
        "pnl_pct": 0.0,
        "positions": [],
    }
