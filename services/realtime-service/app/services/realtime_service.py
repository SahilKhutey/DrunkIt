"""Realtime service: ConnectionManager & Live Streaming Engine."""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from fastapi import WebSocket

from faccp_common.logging import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """Manages active WebSockets connections grouped by channel topic."""

    def __init__(self) -> None:
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, channel: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[channel].append(websocket)
        logger.info("websocket_connected", channel=channel)

    def disconnect(self, channel: str, websocket: WebSocket) -> None:
        if websocket in self.active_connections[channel]:
            self.active_connections[channel].remove(websocket)
            if not self.active_connections[channel]:
                del self.active_connections[channel]
            logger.info("websocket_disconnected", channel=channel)

    async def broadcast(self, channel: str, message: dict[str, Any]) -> None:
        if channel not in self.active_connections:
            return
        payload = json.dumps(message)
        dead = []
        for ws in self.active_connections[channel]:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)

        for ws in dead:
            self.disconnect(channel, ws)

    def get_stats(self) -> tuple[int, int]:
        total_channels = len(self.active_connections)
        total_conns = sum(len(conns) for conns in self.active_connections.values())
        return total_channels, total_conns


manager = ConnectionManager()
