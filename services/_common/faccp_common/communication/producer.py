"""Async Kafka producer with retry and idempotence."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from faccp_common.communication.envelope import EventEnvelope

logger = logging.getLogger(__name__)


class EventProducer:
    """Async Kafka producer with reliability guarantees."""

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
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        if self._producer is not None:
            return
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers,
            client_id=self._client_id,
            security_protocol=self._security_protocol,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8") if not isinstance(v, bytes) else v,
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            enable_idempotence=True,
            acks="all",
            max_in_flight_requests_per_connection=5,
            compression_type="gzip",
            linger_ms=10,
        )
        await self._producer.start()
        logger.info("event_producer.started", extra={"client_id": self._client_id})

    async def stop(self) -> None:
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None

    async def publish(
        self,
        topic: str,
        envelope: EventEnvelope | dict[str, Any],
        key: str | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 10.0,
    ) -> None:
        if self._producer is None:
            raise RuntimeError("Producer not started. Call start() first.")
        if isinstance(envelope, EventEnvelope):
            value = envelope.to_dict()
        else:
            value = envelope
        try:
            kafka_headers = [(k, v.encode("utf-8")) for k, v in (headers or {}).items()]
            kafka_headers.append(
                ("correlation_id", envelope.metadata.correlation_id.encode("utf-8"))
                if isinstance(envelope, EventEnvelope)
                else (b"", )
            )
            kafka_headers.append(
                ("event_type", envelope.event_type.encode("utf-8"))
                if isinstance(envelope, EventEnvelope)
                else (b"", )
            )
            await asyncio.wait_for(
                self._producer.send_and_wait(
                    topic=topic,
                    value=value,
                    key=key,
                    headers=kafka_headers if any(h[1] for h in kafka_headers) else None,
                ),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.error("event_publish.timeout", extra={"topic": topic, "timeout": timeout})
            raise
        except KafkaError:
            logger.exception("event_publish.failed", extra={"topic": topic})
            raise
