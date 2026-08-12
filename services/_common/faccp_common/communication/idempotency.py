"""
Idempotent Event Consumer.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class IdempotentConsumer:
    """Base class for event consumers maintaining event_id deduplication."""

    def __init__(self) -> None:
        self.processed_event_ids: set[str] = set()

    async def is_processed(self, event_id: str) -> bool:
        return event_id in self.processed_event_ids

    async def mark_processed(self, event_id: str) -> None:
        self.processed_event_ids.add(event_id)

    async def process(self, event: dict[str, Any]) -> bool:
        event_id = event.get("event_id")
        if not event_id:
            raise ValueError("Event missing event_id")

        if await self.is_processed(event_id):
            logger.info("event.duplicate_skipped event_id=%s", event_id)
            return False

        await self._handle_event(event)
        await self.mark_processed(event_id)
        return True

    async def _handle_event(self, event: dict[str, Any]) -> None:
        """Override in subclasses to perform domain processing."""
        pass
