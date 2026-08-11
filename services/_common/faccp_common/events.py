from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


def new_event_id() -> str:
    return f"evt_{uuid.uuid4().hex[:24]}"


def new_correlation_id() -> str:
    return f"cor_{uuid.uuid4().hex}"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class EventMetadata(BaseModel):
    """Common metadata attached to every event."""

    correlation_id: str = Field(default_factory=new_correlation_id)
    causation_id: str | None = None
    producer: str
    schema_version: str = "1.0"
    environment: str = "local"
    user_id: str | None = None
    session_id: str | None = None


class Event(BaseModel, Generic[T]):
    """Standard event envelope."""

    event_id: str = Field(default_factory=new_event_id)
    event_type: str
    occurred_at: str = Field(default_factory=utc_now_iso)
    metadata: EventMetadata
    payload: T


def make_event(
    event_type: str,
    payload: Any,
    *,
    producer: str,
    correlation_id: str | None = None,
    causation_id: str | None = None,
    user_id: str | None = None,
    session_id: str | None = None,
    environment: str = "local",
) -> dict[str, Any]:
    """Construct a serialized event envelope."""
    return Event(
        event_type=event_type,
        metadata=EventMetadata(
            correlation_id=correlation_id or new_correlation_id(),
            causation_id=causation_id,
            producer=producer,
            user_id=user_id,
            session_id=session_id,
            environment=environment,
        ),
        payload=payload if isinstance(payload, dict) else payload.model_dump(),
    ).model_dump(mode="json")


class ConsumerCreatedPayload(BaseModel):
    consumer_id: str
    email: str
    phone: str | None = None
    level: str


class ConsumerVerifiedPayload(BaseModel):
    consumer_id: str
    verification_type: str
    result: str
    provider: str | None = None


class RetailerCreatedPayload(BaseModel):
    retailer_id: str
    organization_id: str
    legal_name: str
    level: str


class LicenseUpdatedPayload(BaseModel):
    license_id: str
    retailer_id: str
    status: str
    valid_until: str | None = None


class OrderStateChangedPayload(BaseModel):
    order_id: str
    consumer_id: str
    retailer_id: str
    from_state: str
    to_state: str
    reason: str | None = None


class ComplianceDecisionPayload(BaseModel):
    decision_id: str
    subject_type: str
    subject_id: str
    decision: str
    rule_ids: list[str]
    jurisdiction: str
