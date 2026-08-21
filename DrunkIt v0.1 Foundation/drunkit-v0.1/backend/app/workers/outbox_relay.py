"""Transactional Outbox Relay Worker.

Polls unprocessed domain events from PostgreSQL/SQLite outbox table, converts them
to standardized EventEnvelope payloads, dispatches them to event bus/subscribers,
and marks them as published for reliable at-least-once delivery.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_sync_db
from app.models.audit import OutboxEvent

logger = logging.getLogger("drunkit.workers.outbox")


class OutboxRelayWorker:
    """Reliable outbox event relay engine."""

    def __init__(self, batch_size: int = 50, dispatch_sink: Callable[[dict[str, Any]], None] | None = None):
        self.batch_size = batch_size
        self.dispatch_sink = dispatch_sink or self._default_sink
        self.dispatched_count = 0

    def _default_sink(self, event_envelope: dict[str, Any]) -> None:
        """Default event sink logging structured event payload."""
        logger.info(
            f"Relayed outbox event: {event_envelope['event_type']} [id={event_envelope['id']}] "
            f"aggregate={event_envelope['aggregate_type']}:{event_envelope['aggregate_id']}"
        )

    def process_pending_events(self, session: Session) -> int:
        """Fetch and dispatch a single batch of unpublished outbox events."""
        stmt = (
            select(OutboxEvent)
            .where(OutboxEvent.published_at.is_(None))
            .order_by(OutboxEvent.occurred_at.asc())
            .limit(self.batch_size)
        )
        events = list(session.scalars(stmt).all())

        if not events:
            return 0

        dispatched = 0
        now = datetime.now(timezone.utc)
        for event in events:
            envelope = {
                "id": str(event.id),
                "event_type": event.event_type,
                "aggregate_type": event.aggregate_type,
                "aggregate_id": str(event.aggregate_id),
                "correlation_id": str(event.correlation_id),
                "payload": event.payload,
                "created_at": event.occurred_at.isoformat() if event.occurred_at else now.isoformat(),
            }

            try:
                self.dispatch_sink(envelope)
                event.published_at = now
                dispatched += 1
                self.dispatched_count += 1
            except Exception as ex:
                logger.error(f"Failed to dispatch outbox event {event.id}: {ex}")

        session.flush()
        return dispatched

    async def run_forever(self, interval_seconds: float = 1.0) -> None:
        """Continuous async worker loop polling outbox table."""
        logger.info(f"Starting Outbox Relay Worker (poll interval: {interval_seconds}s)...")
        while True:
            try:
                for session in get_sync_db():
                    count = self.process_pending_events(session)
                    if count > 0:
                        session.commit()
                        logger.debug(f"Dispatched {count} outbox events.")
            except Exception as err:
                logger.error(f"Error in Outbox Relay Worker loop: {err}")
            await asyncio.sleep(interval_seconds)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    worker = OutboxRelayWorker()
    asyncio.run(worker.run_forever())
