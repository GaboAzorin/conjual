"""WebSocket endpoints for real-time updates."""

import asyncio
import json
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Send message to all connected clients."""
        if not self.active_connections:
            return

        data = json.dumps(message)
        disconnected = set()

        for connection in self.active_connections:
            try:
                await connection.send_text(data)
            except Exception:
                disconnected.add(connection)

        # Clean up disconnected clients
        self.active_connections -= disconnected


manager = ConnectionManager()


@router.websocket("/prices")
async def websocket_prices(websocket: WebSocket):
    """WebSocket endpoint for real-time price updates."""
    await manager.connect(websocket)

    try:
        # Send initial prices
        await websocket.send_json({
            "type": "prices",
            "data": {
                "BTC-CLP": {"price": 95000000, "change_24h": 2.5},
                "ETH-CLP": {"price": 3500000, "change_24h": -1.2},
            },
        })

        while True:
            # Wait for messages from client
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)

                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif message.get("type") == "subscribe":
                    # TODO: Handle subscription to specific symbols
                    pass

            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_json({"type": "heartbeat"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/bot")
async def websocket_bot_status(websocket: WebSocket):
    """WebSocket endpoint for real-time bot status updates."""
    await manager.connect(websocket)

    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)

                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

            except asyncio.TimeoutError:
                # Send bot status update
                await websocket.send_json({
                    "type": "bot_status",
                    "data": {
                        "status": "stopped",
                        "last_check": "2026-01-17T12:00:00Z",
                    },
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Helper function to broadcast updates from other parts of the application
async def broadcast_price_update(prices: dict):
    """Broadcast price update to all connected clients."""
    await manager.broadcast({
        "type": "prices",
        "data": prices,
    })


async def broadcast_trade_update(trade: dict):
    """Broadcast trade update to all connected clients."""
    await manager.broadcast({
        "type": "trade",
        "data": trade,
    })


async def broadcast_bot_action(action: dict):
    """Broadcast bot action to all connected clients."""
    await manager.broadcast({
        "type": "bot_action",
        "data": action,
    })
