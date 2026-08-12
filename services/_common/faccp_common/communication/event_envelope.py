"""
Standard Event Envelope.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any


class StandardEvent:
    """Standard event envelope for all asynchronous communication."""

    def __init__(
        self,
        event_type: str,
        producer: str,
        payload: dict[str, Any],
        version: int = 1,
        correlation_id: str | None = None,
        causation_id: str | None = None,
        event_id: str | None = None,
    ) -> None:
        self.event_id = event_id or f"evt_{uuid.uuid4().hex[:16]}"
        self.event_type = event_type
        self.version = version
        self.producer = producer
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.correlation_id = correlation_id or self.event_id
        self.causation_id = causation_id
        self.payload = payload

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "version": self.version,
            "producer": self.producer,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "payload": self.payload,
        }
