"""Standard Event Metadata and Envelope models for FACCP platform."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field


class EventMetadata(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    correlation_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    causation_id: uuid.UUID | None = None
    producer: str
    schema_version: int = 1
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    tenant_id: str | None = None
    actor_id: str | None = None
    trace_id: str | None = None
    request_id: str | None = None


class EventEnvelope(BaseModel):
    """Standard event representation used by every FACCP service."""

    event_type: str
    metadata: EventMetadata
    aggregate_type: str = "order"
    aggregate_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    payload: dict[str, Any]

    @property
    def event_id(self) -> uuid.UUID:
        return self.metadata.event_id

    def to_flat_dict(self) -> dict[str, Any]:
        """Convert to flat dictionary conforming to JSON schema event envelope contract."""
        return {
            "event_id": str(self.metadata.event_id),
            "event_type": self.event_type,
            "schema_version": self.metadata.schema_version,
            "occurred_at": self.metadata.occurred_at.isoformat(),
            "producer": self.metadata.producer,
            "aggregate_type": self.aggregate_type,
            "aggregate_id": str(self.aggregate_id),
            "correlation_id": str(self.metadata.correlation_id),
            "causation_id": str(self.metadata.causation_id or self.metadata.correlation_id),
            "payload": self.payload,
        }


def create_event(
    *,
    event_type: str,
    producer: str,
    aggregate_type: str,
    aggregate_id: str | uuid.UUID,
    correlation_id: str | uuid.UUID,
    payload: dict[str, Any],
    causation_id: str | uuid.UUID | None = None,
    schema_version: int = 1,
) -> EventEnvelope:
    """Create a fully-populated EventEnvelope instance."""
    corr_uuid = uuid.UUID(str(correlation_id)) if isinstance(correlation_id, str) else correlation_id
    caus_uuid = (
        uuid.UUID(str(causation_id))
        if causation_id and isinstance(causation_id, str)
        else (causation_id if isinstance(causation_id, uuid.UUID) else corr_uuid)
    )
    agg_uuid = uuid.UUID(str(aggregate_id)) if isinstance(aggregate_id, str) else aggregate_id

    metadata = EventMetadata(
        event_id=uuid.uuid4(),
        correlation_id=corr_uuid,
        causation_id=caus_uuid,
        producer=producer,
        schema_version=schema_version,
    )
    return EventEnvelope(
        event_type=event_type,
        metadata=metadata,
        aggregate_type=aggregate_type,
        aggregate_id=agg_uuid,
        payload=payload,
    )
