"""AIOKafka Consumer wrapper with manual offset commit and EventEnvelope deserialization."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any
from aiokafka import AIOKafkaConsumer

from faccp_platform.config.settings import get_settings
from .envelope import EventEnvelope
from .idempotency import already_processed, mark_processed
from .serialization import deserialize_event

logger = logging.getLogger("faccp.events.consumer")

EventHandler = Callable[[EventEnvelope], Awaitable[None]]


class EventConsumer:
    """Manual-commit Kafka consumer with enable_auto_commit=False for zero message loss."""

    def __init__(
        self,
        bootstrap_servers: str | None = None,
        topic: str = "faccp.order.events",
        group_id: str = "faccp-consumer-group",
        handler: EventHandler | None = None,
        client_id: str = "faccp-consumer",
    ) -> None:
        settings = get_settings()
        self.bootstrap_servers = bootstrap_servers or settings.kafka_bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.handler = handler
        self.client_id = client_id
        self.consumer: AIOKafkaConsumer | None = None
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        if self._running:
            return
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            client_id=self.client_id,
            enable_auto_commit=False,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")) if v else {},
        )
        try:
            await self.consumer.start()
            self._running = True
            if self.handler is not None:
                self._task = asyncio.create_task(self._consume_loop())
            logger.info(f"EventConsumer started for topic={self.topic}")
        except Exception as exc:
            logger.warning(f"EventConsumer start deferred/offline mode: {exc}")

    async def messages(self) -> AsyncGenerator[Any, None]:
        if self.consumer is not None:
            async for msg in self.consumer:
                yield msg

    async def _consume_loop(self) -> None:
        if self.consumer is None or self.handler is None:
            return
        try:
            async for msg in self.consumer:
                if not self._running:
                    break
                try:
                    event = deserialize_event(msg.value)
                except Exception:
                    event = msg.value
                await self.handler(event)
                await self.consumer.commit()
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error(f"Error in consume loop: {exc}")

    async def stop(self) -> None:
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self.consumer is not None:
            try:
                await self.consumer.stop()
            except Exception:
                pass
            self.consumer = None


class BaseConsumer:
    """Base class for idempotent consumers enforcing DB transaction + mark_processed before offset commit."""

    consumer_name: str = "base-consumer"

    def __init__(self, session: Any) -> None:
        self.session = session

    async def handle(self, event: Any) -> None:
        event_id = getattr(event, "event_id", None)
        if event_id is None and isinstance(event, dict):
            metadata = event.get("metadata", {})
            event_id = metadata.get("event_id") or event.get("event_id")

        if event_id is not None:
            if await already_processed(self.session, event_id, self.consumer_name):
                logger.info(f"Skipping already processed event: {event_id} by {self.consumer_name}")
                return

        # Execute subclass business processing logic
        await self.process(event)

        if event_id is not None and self.session is not None:
            await mark_processed(self.session, event_id, self.consumer_name)

    async def process(self, event: Any) -> None:
        """Subclasses override this method to perform business logic."""
        raise NotImplementedError
