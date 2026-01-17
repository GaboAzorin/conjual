"""Trades endpoints."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.core.database import get_db
from app.models.trade import Trade, TradeSide, TradeStatus
from app.models.user import User

router = APIRouter()


class TradeResponse(BaseModel):
    id: int
    exchange: str
    symbol: str
    side: TradeSide
    status: TradeStatus
    amount: Decimal
    price: Decimal
    total: Decimal
    fee: Decimal
    strategy: Optional[str]
    reason: Optional[str]
    created_at: datetime
    executed_at: Optional[datetime]

    class Config:
        from_attributes = True


class TradeListResponse(BaseModel):
    trades: list[TradeResponse]
    total: int
    page: int
    page_size: int


@router.get("/", response_model=TradeListResponse)
async def get_trades(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    symbol: Optional[str] = None,
    side: Optional[TradeSide] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get trade history."""
    query = select(Trade).where(Trade.user_id == current_user.id)

    if symbol:
        query = query.where(Trade.symbol == symbol)
    if side:
        query = query.where(Trade.side == side)

    # Order by most recent first
    query = query.order_by(Trade.created_at.desc())

    # Pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    trades = result.scalars().all()

    # Get total count
    count_query = select(Trade).where(Trade.user_id == current_user.id)
    if symbol:
        count_query = count_query.where(Trade.symbol == symbol)
    if side:
        count_query = count_query.where(Trade.side == side)

    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())

    return TradeListResponse(
        trades=trades,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(
    trade_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific trade."""
    result = await db.execute(
        select(Trade).where(Trade.id == trade_id, Trade.user_id == current_user.id)
    )
    trade = result.scalar_one_or_none()

    if not trade:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Trade not found")

    return trade
