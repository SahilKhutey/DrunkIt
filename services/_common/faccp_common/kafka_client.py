from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

try:
    from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
    from aiokafka.errors import KafkaError
except ModuleNotFoundError:  # pragma: no cover - exercised in lean local envs
    AIOKafkaConsumer = None  # type: ignore[assignment]
    AIOKafkaProducer = None  # type: ignore[assignment]
    KafkaError = Exception  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class EventProducer:
    """Async Kafka producer with JSON serialization."""

    def __init__(
        self,
        bootstrap_servers: list[str],
        client_id: str,
        security_protocol: str = "PLAINTEXT",
    ) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._client_id = client_id
        self._security_protocol = security_protocol
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        if AIOKafkaProducer is None:
            raise RuntimeError("aiokafka is not installed; Kafka producer is unavailable.")
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            client_id=self._client_id,
            security_protocol=self._security_protocol,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            enable_idempotence=True,
            acks="all",
            compression_type="gzip",
        )
        await self._producer.start()
        logger.info("Kafka producer started for %s", self._client_id)

    async def stop(self) -> None:
        if self._producer is not None:
            await self._producer.stop()

    async def publish(
        self,
        topic: str,
        payload: dict[str, Any],
        key: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        if self._producer is None:
            raise RuntimeError("Producer not started.")
        try:
            kafka_headers = [(k, v.encode("utf-8")) for k, v in (headers or {}).items()]
            await self._producer.send_and_wait(
                topic=topic,
                value=payload,
                key=key,
                headers=kafka_headers,
            )
        except KafkaError:
            logger.exception("Failed to publish event to topic %s", topic)
            raise


class EventConsumer:
    """Async Kafka consumer base class."""

    def __init__(
        self,
        bootstrap_servers: list[str],
        group_id: str,
        topics: list[str],
        client_id: str,
    ) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._group_id = group_id
        self._topics = topics
        self._client_id = client_id
        self._consumer: AIOKafkaConsumer | None = None

    async def start(self) -> None:
        if AIOKafkaConsumer is None:
            raise RuntimeError("aiokafka is not installed; Kafka consumer is unavailable.")
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
        )
        await self._consumer.start()
        logger.info(
            "Kafka consumer started: group=%s topics=%s", self._group_id, self._topics
        )

    async def stop(self) -> None:
        if self._consumer is not None:
            await self._consumer.stop()

    async def consume(self) -> AsyncIterator[tuple[str, str | None, dict[str, Any]]]:
        if self._consumer is None:
            raise RuntimeError("Consumer not started.")
        async for msg in self._consumer:
            try:
                yield msg.topic, msg.key, msg.value
                await self._consumer.commit()
            except Exception:
                logger.exception("Error processing message from %s", msg.topic)
