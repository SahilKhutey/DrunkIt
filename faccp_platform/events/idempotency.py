"""Consumer idempotency service for event deduplication."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from faccp_platform.database.models import ProcessedEvent


class EventIdempotency:
    """Checks and records processed event IDs within transactional boundaries."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def already_processed(self, event_id: str | uuid.UUID, consumer: str | None = None) -> bool:
        """Check if an event ID has already been processed by consumer."""
        return await already_processed(self.session, event_id, consumer)

    async def mark_processed(self, event_id: str | uuid.UUID, consumer: str = "default") -> ProcessedEvent:
        """Mark an event ID as processed by a given consumer."""
        return await mark_processed(self.session, event_id, consumer)


async def already_processed(
    session: Any, event_id: str | uuid.UUID, consumer_name: str | None = None
) -> bool:
    """Check if event_id was already processed (or by consumer_name if specified)."""
    if session is None:
        return False
    event_str = str(event_id)
    stmt = select(ProcessedEvent.id).where(ProcessedEvent.event_id == event_str)
    if consumer_name and consumer_name != "default":
        stmt = stmt.where(ProcessedEvent.consumer == consumer_name)
    stmt = stmt.limit(1)
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None


async def mark_processed(
    session: Any, event_id: str | uuid.UUID, consumer_name: str = "default"
) -> ProcessedEvent | None:
    """Mark event_id as processed by consumer_name in DB transaction."""
    if session is None:
        return None
    event_str = str(event_id)
    record = ProcessedEvent(
        event_id=event_str,
        consumer=consumer_name,
        processed_at=datetime.now(timezone.utc),
    )
    session.add(record)
    await session.flush()
    return record
