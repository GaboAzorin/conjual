"""Portfolio model for tracking balances."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Portfolio(Base):
    """Portfolio snapshot model."""

    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Balances
    balance_clp: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)
    balance_btc: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=0)
    balance_eth: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=0)

    # Calculated values
    total_value_clp: Mapped[Decimal] = mapped_column(Numeric(20, 2), default=0)

    # Exchange source
    exchange: Mapped[str] = mapped_column(String(50), default="buda")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
