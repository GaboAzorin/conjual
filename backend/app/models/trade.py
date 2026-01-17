"""Trade model for executed trades."""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TradeSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class TradeStatus(str, Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Trade(Base):
    """Executed trade record."""

    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Trade details
    exchange: Mapped[str] = mapped_column(String(50))
    symbol: Mapped[str] = mapped_column(String(20))  # e.g., "BTC-CLP"
    side: Mapped[TradeSide] = mapped_column(SQLEnum(TradeSide))
    status: Mapped[TradeStatus] = mapped_column(SQLEnum(TradeStatus), default=TradeStatus.PENDING)

    # Amounts
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    price: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    total: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    fee: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=0)

    # Strategy info
    strategy: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Exchange reference
    exchange_order_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
