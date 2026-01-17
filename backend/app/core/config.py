"""
Application configuration using Pydantic Settings.
All sensitive values should be set via environment variables.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Application
    APP_NAME: str = "Conjual"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/conjual"

    # JWT Authentication
    JWT_SECRET_KEY: str = "CHANGE-THIS-IN-PRODUCTION-USE-SECURE-KEY"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:8081", "http://localhost:19006"]

    # Exchange - Buda.com
    BUDA_API_KEY: str = ""
    BUDA_API_SECRET: str = ""

    # Exchange - Binance (for data collection)
    BINANCE_API_KEY: str = ""
    BINANCE_API_SECRET: str = ""

    # Trading Configuration
    TRADING_ENABLED: bool = False  # Safety: disabled by default
    PAPER_TRADING: bool = True  # Start with paper trading
    MAX_SINGLE_TRADE_PCT: float = 0.25  # 25% max per trade
    MAX_DAILY_LOSS_PCT: float = 0.10  # 10% daily loss limit
    MIN_BALANCE_CLP: int = 5000  # Always keep 5000 CLP

    # Data Collection
    DATA_COLLECTION_ENABLED: bool = True
    DATA_DIR: str = "data"

    # Monitoring (Optional)
    SENTRY_DSN: str = ""

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
