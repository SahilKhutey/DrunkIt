"""Transactional Outbox background worker."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import select
from faccp_platform.database.models import EventOutbox
from .producer import EventProducer

logger = logging.getLogger("faccp.events.outbox_worker")


class OutboxWorker:
    """Worker background job processing and publishing queued transactional outbox events."""

    def __init__(self, session_factory: Any, producer: EventProducer) -> None:
        self.session_factory = session_factory
        self.producer = producer

    async def publish_batch(self, limit: int = 100) -> int:
        """Fetch pending outbox records and publish to Kafka. Sets status='published' only after confirmation."""
        async with self.session_factory() as session:
            stmt = (
                select(EventOutbox)
                .where(EventOutbox.status == "pending")
                .order_by(EventOutbox.created_at)
                .limit(limit)
            )
            result = await session.execute(stmt)
            records = result.scalars().all()

            published_count = 0
            for record in records:
                try:
                    payload = json.loads(record.payload) if isinstance(record.payload, str) else record.payload
                    await self.producer.publish(record.topic, payload, key=record.event_id)
                    record.status = "published"
                    record.published_at = datetime.now(timezone.utc)
                    published_count += 1
                except Exception as exc:
                    logger.warning(f"Outbox publish failed for event_id={record.event_id}: {exc}")
                    record.attempts += 1
                    record.last_error = str(exc)
                    if record.attempts >= 5:
                        record.status = "failed"
            await session.commit()
            return published_count

    async def run(self) -> int:
        """Execute outbox publish loop iteration."""
        return await self.publish_batch()
