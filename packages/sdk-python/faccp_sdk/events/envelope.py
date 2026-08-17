"""
FACCP Canonical Event Envelope
================================
Every domain event published to Kafka MUST use this envelope.

Fields enable:
  - Idempotency:           event_id          (deduplicate on consumer side)
  - Distributed tracing:   correlation_id    (propagated from HTTP request)
  - Causal chain:          causation_id      (parent event_id that caused this)
  - Optimistic locking:    aggregate_version (detect out-of-order processing)
  - Schema evolution:      schema_version    (breaking changes get new version)

TypeScript counterpart: packages/event-contracts/src/events.ts -> DomainEvent<T>

Usage
-----
    from faccp_sdk.events.envelope import EventEnvelope

    envelope = EventEnvelope(
        event_id=uuid4(),
        event_type="order.created.v1",
        aggregate_id=order_id,
        aggregate_version=1,
        correlation_id=request_context.correlation_id,
        causation_id=request_context.request_id,
        producer="order-service",
        payload={"order_id": str(order_id), "status": "CREATED"},
    )
    await kafka_client.publish(topic="order.created", envelope=envelope)

Validation
----------
The constitution check at scripts/constitution/check_compliance.py enforces
that all Kafka publish calls use EventEnvelope (or a subclass).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator


class EventEnvelope(BaseModel):
    """Canonical FACCP domain event envelope. All Kafka events must use this."""

    model_config = {"frozen": True}

    # ── Identity ──────────────────────────────────────────────────────────────
    event_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="UUID v4 unique per event instance. Use for consumer-side deduplication.",
    )

    event_type: str = Field(
        description=(
            "Fully-qualified event type in dot notation: "
            "'<domain>.<event>.<version>' e.g. 'order.created.v1'."
        ),
    )

    schema_version: str = Field(
        default="1.0",
        description="Schema version string. Increment on breaking payload changes.",
    )

    # ── Aggregate ─────────────────────────────────────────────────────────────
    aggregate_id: uuid.UUID = Field(
        description="The domain aggregate this event belongs to (e.g. an order UUID).",
    )

    aggregate_version: int = Field(
        ge=1,
        description="Monotonic version of the aggregate at the time this event was emitted.",
    )

    # ── Causality & Tracing ───────────────────────────────────────────────────
    correlation_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description=(
            "Propagated from the originating HTTP request. "
            "Ties together all events produced by a single user request across services."
        ),
    )

    causation_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description=(
            "The event_id (or request ID) of the event that directly caused this one. "
            "Forms a causal chain for event replay and debugging."
        ),
    )

    # ── Provenance ────────────────────────────────────────────────────────────
    producer: str = Field(
        description="Publishing service identifier e.g. 'order-service'.",
    )

    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the event occurred in the domain.",
    )

    # ── Payload ───────────────────────────────────────────────────────────────
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Domain-specific event payload. Must be JSON-serializable.",
    )

    # ── Validators ────────────────────────────────────────────────────────────
    @field_validator("event_type")
    @classmethod
    def event_type_must_be_namespaced(cls, v: str) -> str:
        parts = v.split(".")
        if len(parts) < 3:
            raise ValueError(
                f"event_type '{v}' must follow '<domain>.<event>.<version>' "
                "e.g. 'order.created.v1'"
            )
        if not parts[-1].startswith("v") or not parts[-1][1:].isdigit():
            raise ValueError(
                f"event_type '{v}' must end with a version suffix like 'v1', 'v2'"
            )
        return v

    @field_validator("schema_version")
    @classmethod
    def schema_version_format(cls, v: str) -> str:
        parts = v.split(".")
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            raise ValueError(
                f"schema_version '{v}' must be in '<major>.<minor>' format e.g. '1.0'"
            )
        return v

    # ── Serialization helpers ─────────────────────────────────────────────────
    def to_kafka_value(self) -> dict[str, Any]:
        """Return a JSON-serializable dict for Kafka message value."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "schema_version": self.schema_version,
            "aggregate_id": str(self.aggregate_id),
            "aggregate_version": self.aggregate_version,
            "correlation_id": str(self.correlation_id),
            "causation_id": str(self.causation_id),
            "producer": self.producer,
            "occurred_at": self.occurred_at.isoformat(),
            "payload": self.payload,
        }

    def to_kafka_headers(self) -> list[tuple[str, bytes]]:
        """Return Kafka message headers for routing and tracing."""
        return [
            ("event_type", self.event_type.encode()),
            ("schema_version", self.schema_version.encode()),
            ("correlation_id", str(self.correlation_id).encode()),
            ("producer", self.producer.encode()),
        ]

    @classmethod
    def from_kafka_value(cls, data: dict[str, Any]) -> "EventEnvelope":
        """Deserialize an EventEnvelope from a Kafka message value dict."""
        return cls(**data)
