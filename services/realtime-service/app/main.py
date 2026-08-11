"""
Real-time gateway — WebSocket connections for live tracking, order updates, and driver location streaming.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

import redis.asyncio as redis
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app, Counter, Gauge

from faccp_common.config import BaseServiceSettings
from faccp_common.kafka_client import EventConsumer
from faccp_common.middleware import register_exception_handlers, register_middleware
from faccp_common.security import decode_token
from faccp_common.logging import configure_logging, get_logger


class RealtimeSettings(BaseServiceSettings):
    service_name: str = "faccp-realtime"
    port: int = 8016
    redis_url: str = "redis://localhost:6379/15"
    max_connections_per_user: int = 5
    heartbeat_interval_seconds: int = 30


settings = RealtimeSettings()
configure_logging(settings.service_name, settings.service_version, settings.environment)
logger = get_logger(__name__)

ACTIVE_CONNECTIONS = Gauge("realtime_active_connections", "Active WebSocket connections", ["type"])
MESSAGES_SENT = Counter("realtime_messages_sent_total", "Messages sent", ["type"])
MESSAGES_RECEIVED = Counter("realtime_messages_received_total", "Messages received", ["type"])


class ConnectionManager:

    def __init__(self) -> None:
        self.channels: dict[str, set[WebSocket]] = {}
        self.user_connections: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()
        self.max_per_user = settings.max_connections_per_user

    async def connect(self, websocket: WebSocket, channel: str, user_id: str) -> bool:
        if len(self.user_connections.get(user_id, set())) >= self.max_per_user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return False
        await websocket.accept()
        async with self._lock:
            self.channels.setdefault(channel, set()).add(websocket)
            self.user_connections.setdefault(user_id, set()).add(websocket)
            ACTIVE_CONNECTIONS.labels(type=channel.split(":")[0] if ":" in channel else "general").inc()
            logger.info("websocket.connected", channel=channel, user_id=user_id)
        return True

    async def disconnect(self, websocket: WebSocket, channel: str, user_id: str) -> None:
        async with self._lock:
            self.channels.get(channel, set()).discard(websocket)
            self.user_connections.get(user_id, set()).discard(websocket)
            if not self.user_connections.get(user_id):
                self.user_connections.pop(user_id, None)
            if not self.channels.get(channel):
                self.channels.pop(channel, None)
            ACTIVE_CONNECTIONS.labels(type=channel.split(":")[0] if ":" in channel else "general").dec()
            logger.info("websocket.disconnected", channel=channel, user_id=user_id)

    async def broadcast_to_channel(self, channel: str, message: dict[str, Any]) -> int:
        connections = list(self.channels.get(channel, set()))
        payload = json.dumps(message, default=str)
        delivered = 0
        for ws in connections:
            try:
                await ws.send_text(payload)
                delivered += 1
            except Exception:
                pass
        MESSAGES_SENT.labels(type=channel.split(":")[0] if ":" in channel else "general").inc(delivered)
        return delivered

    async def send_to_user(self, user_id: str, message: dict[str, Any]) -> int:
        connections = list(self.user_connections.get(user_id, set()))
        payload = json.dumps(message, default=str)
        delivered = 0
        for ws in connections:
            try:
                await ws.send_text(payload)
                delivered += 1
            except Exception:
                pass
        return delivered

    def stats(self) -> dict[str, Any]:
        return {
            "total_channels": len(self.channels),
            "total_users": len(self.user_connections),
            "total_connections": sum(len(c) for c in self.user_connections.values()),
        }


manager = ConnectionManager()
redis_client: redis.Redis | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    global redis_client
    redis_client = redis.from_url(str(settings.redis_url), decode_responses=True)
    consumer_task = asyncio.create_task(consume_and_broadcast())
    yield
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
    await redis_client.aclose()


async def consume_and_broadcast() -> None:
    consumer = EventConsumer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id="realtime-broadcaster",
        topics=["order.events", "delivery.events", "compliance.events", "risk.events"],
        client_id="faccp-realtime-broadcaster",
    )
    await consumer.start()
    try:
        async for topic, key, value in consumer.consume():
            try:
                await route_event_to_channel(topic, value)
            except Exception:
                logger.exception("broadcast_failed", topic=topic)
    finally:
        await consumer.stop()


async def route_event_to_channel(topic: str, event: dict[str, Any]) -> None:
    event_type = event.get("event_type", "")
    payload = event.get("payload", {})
    if topic == "order.events":
        order_id = payload.get("order_id")
        if not order_id: return
        channel = f"order:{order_id}"
        message = {"type": event_type, "order_id": order_id, "data": payload, "occurred_at": event.get("occurred_at")}
        await manager.broadcast_to_channel(channel, message)
        if payload.get("consumer_id"):
            await manager.broadcast_to_channel(f"consumer:{payload['consumer_id']}", message)
        if payload.get("store_id"):
            await manager.broadcast_to_channel(f"store:{payload['store_id']}", message)
    elif topic == "delivery.events":
        delivery_id = payload.get("delivery_id")
        if not delivery_id: return
        channel = f"delivery:{delivery_id}"
        message = {"type": event_type, "delivery_id": delivery_id, "data": payload, "occurred_at": event.get("occurred_at")}
        await manager.broadcast_to_channel(channel, message)
    elif topic in ("compliance.events", "risk.events"):
        await manager.broadcast_to_channel("admin:alerts", {
            "type": event_type, "data": payload, "occurred_at": event.get("occurred_at"),
        })


def _authenticate_ws_token(token: str) -> dict[str, Any] | None:
    try:
        return decode_token(
            token, secret=settings.jwt_secret, algorithm=settings.jwt_algorithm,
            issuer=settings.jwt_issuer, audience=settings.jwt_audience, expected_type="access",
        )
    except Exception:
        return None


def create_app() -> FastAPI:
    app = FastAPI(title="FACCP Real-time Gateway", version=settings.service_version, lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    register_exception_handlers(app)
    app.mount("/metrics", make_asgi_app())

    @app.get("/health")
    async def health():
        return {"status": "ok", "service": settings.service_name}

    @app.get("/stats")
    async def stats_endpoint():
        return manager.stats()

    @app.websocket("/ws/{channel}")
    async def websocket_endpoint(websocket: WebSocket, channel: str, token: str = Query(...)):
        claims = _authenticate_ws_token(token)
        if not claims:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        user_id = claims.get("sub", "")
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        if not await manager.connect(websocket, channel, user_id):
            return

        try:
            await websocket.send_json({
                "type": "hello", "channel": channel, "user_id": user_id,
                "server_time": datetime.now(timezone.utc).isoformat(),
            })
            while True:
                try:
                    msg = await asyncio.wait_for(
                        websocket.receive_text(), timeout=settings.heartbeat_interval_seconds * 2
                    )
                    MESSAGES_RECEIVED.labels(type=channel.split(":")[0] if ":" in channel else "general").inc()
                    data = json.loads(msg)
                    if data.get("type") == "ping":
                        await websocket.send_json({"type": "pong", "ts": datetime.now(timezone.utc).isoformat()})
                except asyncio.TimeoutError:
                    await websocket.send_json({"type": "heartbeat", "ts": datetime.now(timezone.utc).isoformat()})
        except WebSocketDisconnect:
            pass
        finally:
            await manager.disconnect(websocket, channel, user_id)

    return app


app = create_app()
