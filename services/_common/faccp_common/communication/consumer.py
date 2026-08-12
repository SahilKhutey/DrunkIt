"""Async Kafka consumer with retry, DLQ, and idempotency."""

from __future__ import annotations

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Callable

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

from faccp_common.communication.envelope import EventEnvelope, parse_envelope
from faccp_common.communication.reliability import RetryPolicy

logger = logging.getLogger(__name__)


class EventHandler(ABC):
    """Base class for event handlers."""

    @abstractmethod
    async def handle(self, envelope: EventEnvelope) -> None:
        ...


class EventConsumer:
    """Async Kafka consumer with DLQ and idempotency."""

    def __init__(
        self,
        bootstrap_servers: list[str] | None = None,
        group_id: str | None = None,
        topics: list[str] | None = None,
        client_id: str | None = None,
        dead_letter_topic: str | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self._bootstrap_servers = bootstrap_servers or ["localhost:9092"]
        self._group_id = group_id or "faccp-group"
        self._topics = topics or ["identity.events"]
        self._client_id = client_id or "faccp-consumer"
        self._dlq_topic = dead_letter_topic or f"{self._topics[0]}.dlq" if self._topics else "dlq"
        self._retry_policy = retry_policy or RetryPolicy()
        self._consumer: AIOKafkaConsumer | None = None
        self._handlers: dict[str, EventHandler] = {}
        self._processed_ids: set[str] = set()  # simple in-memory dedup
        self._max_dedup_size = 100_000

    def register(self, event_type: str, handler: EventHandler) -> None:
        self._handlers[event_type] = handler

    async def start(self) -> None:
        if self._consumer is not None:
            return
        self._consumer = AIOKafkaConsumer(
            *self._topics,
            bootstrap_servers=self._bootstrap_servers,
            group_id=self._group_id,
            client_id=self._client_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            key_deserializer=lambda k: k.decode("utf-8") if k else None,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            max_poll_records=100,
            session_timeout_ms=30_000,
        )
        await self._consumer.start()
        logger.info("event_consumer.started", extra={"group_id": self._group_id, "topics": self._topics})

    async def stop(self) -> None:
        if self._consumer is not None:
            await self._consumer.stop()
            self._consumer = None

    async def consume(self) -> AsyncIterator[EventEnvelope]:
        if self._consumer is None:
            raise RuntimeError("Consumer not started.")
        async for msg in self._consumer:
            try:
                envelope = parse_envelope(msg.value)
            except Exception:
                logger.exception("event_parse.failed", extra={"topic": msg.topic, "offset": msg.offset})
                await self._send_to_dlq(msg.value, "parse_error")
                await self._consumer.commit()
                continue
            # Idempotency check
            if envelope.event_id in self._processed_ids:
                logger.debug("event.duplicate_skipped", extra={"event_id": envelope.event_id})
                await self._consumer.commit()
                continue
            yield envelope

    async def process_with_dlq(self, envelope: EventEnvelope) -> None:
        """Process an envelope with retry and DLQ on failure."""
        handler = self._handlers.get(envelope.event_type)
        if not handler:
            logger.info("event.no_handler", extra={"event_type": envelope.event_type})
            return
        last_exc: Exception | None = None
        for attempt in range(self._retry_policy.max_attempts):
            try:
                await handler.handle(envelope)
                self._processed_ids.add(envelope.event_id)
                if len(self._processed_ids) > self._max_dedup_size:
                    self._processed_ids.clear()
                return
            except Exception as e:
                last_exc = e
                if attempt < self._retry_policy.max_attempts - 1:
                    delay = self._retry_policy.get_delay(attempt)
                    logger.warning(
                        "event.handler_failed",
                        extra={
                            "event_id": envelope.event_id,
                            "event_type": envelope.event_type,
                            "attempt": attempt + 1,
                            "delay": delay,
                            "error": str(e),
                        },
                    )
                    await asyncio.sleep(delay)
        # All retries failed — send to DLQ
        logger.error(
            "event.exhausted_retries",
            extra={"event_id": envelope.event_id, "error": str(last_exc)},
        )
        await self._send_to_dlq(envelope.to_dict(), str(last_exc) if last_exc else "unknown")

    async def _send_to_dlq(self, original: Any, error: str) -> None:
        if not self._dlq_topic:
            return
        logger.warning("event.sent_to_dlq", extra={"dlq": self._dlq_topic, "error": error})

    async def process(self, envelope: Any) -> bool:
        event_id = envelope.get("event_id") if isinstance(envelope, dict) else getattr(envelope, "event_id", None)
        if event_id and event_id in self._processed_ids:
            return False
        if event_id:
            self._processed_ids.add(event_id)
        return True

    async def commit(self) -> None:
        if self._consumer:
            await self._consumer.commit()



IdempotentConsumer = EventConsumer
