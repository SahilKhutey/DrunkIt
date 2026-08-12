"""Standard event envelope for all async communication."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def new_event_id() -> str:
    return f"evt_{uuid.uuid4().hex[:24]}"


def new_correlation_id() -> str:
    return f"corr_{uuid.uuid4().hex[:16]}"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class EventMetadata:
    """Common metadata attached to every event."""

    correlation_id: str = field(default_factory=new_correlation_id)
    causation_id: str | None = None
    producer: str = ""
    schema_version: str = "1.0"
    environment: str = "local"
    user_id: str | None = None
    session_id: str | None = None
    tenant_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "producer": self.producer,
            "schema_version": self.schema_version,
            "environment": self.environment,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "tenant_id": self.tenant_id,
        }


@dataclass
class EventEnvelope:
    """Standard event envelope used by every async message."""

    event_id: str = field(default_factory=new_event_id)
    event_type: str = "event.generic"
    occurred_at: str = field(default_factory=utc_now_iso)
    metadata: EventMetadata = field(default_factory=EventMetadata)
    payload: dict[str, Any] = field(default_factory=dict)
    producer: str = ""

    def __post_init__(self):
        if self.producer and not self.metadata.producer:
            self.metadata.producer = self.producer

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at,
            "producer": self.metadata.producer or self.producer,
            "metadata": self.metadata.to_dict(),
            "payload": self.payload,
        }


    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str, separators=(",", ":"))

    @classmethod
    def from_json(cls, raw: str | bytes) -> "EventEnvelope":
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        data = json.loads(raw)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EventEnvelope":
        metadata = EventMetadata(**data.get("metadata", {}))
        return cls(
            event_id=data["event_id"],
            event_type=data["event_type"],
            occurred_at=data["occurred_at"],
            metadata=metadata,
            payload=data.get("payload", {}),
        )


StandardEvent = EventEnvelope


def create_envelope(
    event_type: str,
    payload: dict[str, Any],
    *,
    producer: str,
    correlation_id: str | None = None,
    causation_id: str | None = None,
    user_id: str | None = None,
    session_id: str | None = None,
    tenant_id: str | None = None,
    environment: str = "local",
) -> EventEnvelope:
    """Build a new event envelope ready to publish."""
    return EventEnvelope(
        event_id=new_event_id(),
        event_type=event_type,
        occurred_at=utc_now_iso(),
        metadata=EventMetadata(
            correlation_id=correlation_id or new_correlation_id(),
            causation_id=causation_id,
            producer=producer,
            environment=environment,
            user_id=user_id,
            session_id=session_id,
            tenant_id=tenant_id,
        ),
        payload=payload,
    )


def parse_envelope(raw: str | bytes | dict[str, Any]) -> EventEnvelope:
    if isinstance(raw, dict):
        return EventEnvelope.from_dict(raw)
    return EventEnvelope.from_json(raw)
