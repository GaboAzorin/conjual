"""OHLCV data model for historical price data."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class OHLCVData(Base):
    """OHLCV (Open, High, Low, Close, Volume) historical data."""

    __tablename__ = "ohlcv_data"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Identifiers
    exchange: Mapped[str] = mapped_column(String(50), index=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    timeframe: Mapped[str] = mapped_column(String(10), index=True)  # 1m, 5m, 1h, 1d, etc.

    # OHLCV data
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    open: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    high: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    low: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    close: Mapped[Decimal] = mapped_column(Numeric(20, 8))
    volume: Mapped[Decimal] = mapped_column(Numeric(20, 8))

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("exchange", "symbol", "timeframe", "timestamp", name="uq_ohlcv"),
        Index("idx_ohlcv_lookup", "exchange", "symbol", "timeframe", "timestamp"),
    )
