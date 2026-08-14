"""Transactional Outbox service for atomic event publishing."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_platform.database.models import EventOutbox
from .envelope import EventEnvelope
from .producer import EventProducer


class OutboxService:
    """Enqueues events in database transaction and processes pending outbox records."""

    def __init__(self, session: AsyncSession, producer: EventProducer | None = None) -> None:
        self.session = session
        self.producer = producer

    async def enqueue(self, *, topic: str, event: EventEnvelope) -> EventOutbox:
        """Write event record to event_outbox table in current transaction."""
        payload_str = json.dumps(event.model_dump(mode="json"))
        record = EventOutbox(
            event_id=str(event.event_id),
            topic=topic,
            event_type=event.event_type,
            payload=payload_str,
            status="pending",
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def process_pending(self, limit: int = 50) -> int:
        """Process and publish pending outbox records."""
        if self.producer is None:
            return 0

        stmt = (
            select(EventOutbox)
            .where(EventOutbox.status == "pending")
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        published_count = 0
        for record in records:
            try:
                event_data = json.loads(record.payload)
                await self.producer.publish(record.topic, event_data)
                record.status = "published"
                record.published_at = datetime.now(timezone.utc)
                published_count += 1
            except Exception as exc:
                record.attempts += 1
                record.last_error = str(exc)
                if record.attempts >= 5:
                    record.status = "failed"
            await self.session.flush()

        return published_count


async def enqueue_event(
    session: Any,
    *,
    topic: str,
    event_type: str,
    aggregate_id: Any,
    payload: dict[str, Any],
) -> EventOutbox | None:
    """Write an outbox event in the active DB transaction."""
    if session is None:
        return None

    event_id = str(uuid.uuid4())
    payload_str = json.dumps(payload)
    record = EventOutbox(
        event_id=event_id,
        topic=topic,
        event_type=event_type,
        payload=payload_str,
        status="pending",
    )
    session.add(record)
    await session.flush()
    return record
