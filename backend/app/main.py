"""
Conjual - Entry Point
Sistema de Trading Inteligente Autónomo
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.v1 import auth, bot, market, portfolio, trades
from app.api.websocket import router as ws_router
from app.core.config import settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Conjual Trading System...")
    await init_db()
    logger.success("Database initialized")

    # TODO: Start data collection scheduler
    # TODO: Start trading engine (if enabled)

    yield

    # Shutdown
    logger.info("Shutting down Conjual...")
    # TODO: Stop trading engine gracefully
    # TODO: Close exchange connections


app = FastAPI(
    title="Conjual",
    description="Sistema de Trading Inteligente Autónomo",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(portfolio.router, prefix="/api/v1/portfolio", tags=["portfolio"])
app.include_router(trades.router, prefix="/api/v1/trades", tags=["trades"])
app.include_router(market.router, prefix="/api/v1/market", tags=["market"])
app.include_router(bot.router, prefix="/api/v1/bot", tags=["bot"])
app.include_router(ws_router, prefix="/ws", tags=["websocket"])


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "conjual",
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Conjual",
        "description": "Sistema de Trading Inteligente Autónomo",
        "docs": "/docs",
        "health": "/health",
    }
