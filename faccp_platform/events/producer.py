"""AIOKafka Producer wrapper with lifecycle management and EventEnvelope serialization."""

from __future__ import annotations

import json
import logging
from typing import Any
from aiokafka import AIOKafkaProducer

from faccp_platform.config.settings import get_settings
from .envelope import EventEnvelope
from .serialization import serialize_event

logger = logging.getLogger("faccp.events.producer")


class EventProducer:
    """Centralized AIOKafka producer for all platform services."""

    def __init__(self, bootstrap_servers: str | None = None) -> None:
        settings = get_settings()
        self.bootstrap_servers = bootstrap_servers or settings.kafka_bootstrap_servers
        self.client_id = settings.kafka_client_id
        self.security_protocol = settings.kafka_security_protocol
        self.request_timeout_ms = settings.kafka_request_timeout_ms
        self.producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        if self.producer is None:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=self.client_id,
                security_protocol=self.security_protocol,
                request_timeout_ms=self.request_timeout_ms,
                value_serializer=lambda value: json.dumps(value).encode("utf-8") if isinstance(value, dict) else value,
            )
            try:
                await self.producer.start()
                logger.info("EventProducer started successfully")
            except Exception as exc:
                logger.warning(f"EventProducer start deferred/offline mode: {exc}")

    async def stop(self) -> None:
        if self.producer is not None:
            try:
                await self.producer.stop()
            except Exception:
                pass
            self.producer = None

    async def publish(
        self, topic: str, event: EventEnvelope | dict[str, Any], key: str | None = None
    ) -> None:
        """Serialize and publish an EventEnvelope or dict to Kafka."""
        if isinstance(event, EventEnvelope):
            payload = serialize_event(event)
            event_key = (key or str(event.aggregate_id or event.event_id)).encode("utf-8")
        else:
            payload = json.dumps(event).encode("utf-8")
            event_key = (key or str(event.get("aggregate_id", ""))).encode("utf-8")

        if self.producer is not None:
            await self.producer.send_and_wait(topic, key=event_key, value=payload)
        else:
            logger.info(f"Published event (simulated): topic={topic} key={event_key.decode('utf-8', errors='ignore')}")
