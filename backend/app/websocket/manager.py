from typing import Any

import socketio

from app.core.logging import get_logger

logger = get_logger(__name__)

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


class ConnectionManager:
    """Thin wrapper around the python-socketio server used to broadcast events."""

    def __init__(self, server: socketio.AsyncServer) -> None:
        self.server = server

    async def broadcast_alert(self, payload: dict[str, Any]) -> None:
        await self.server.emit("alert", payload)

    async def broadcast_new_article(self, payload: dict[str, Any]) -> None:
        await self.server.emit("new_article", payload)

    async def broadcast(self, event: str, payload: dict[str, Any]) -> None:
        await self.server.emit(event, payload)


manager = ConnectionManager(sio)


@sio.event
async def connect(sid: str, environ: dict[str, Any]) -> None:
    logger.info("WebSocket client connected: %s", sid)


@sio.event
async def disconnect(sid: str) -> None:
    logger.info("WebSocket client disconnected: %s", sid)
