"""
Unit tests for the canonical FACCP EventEnvelope.
These tests are part of the event idempotency contract enforcement.
"""

from __future__ import annotations

import uuid
from datetime import timezone

import pytest
from pydantic import ValidationError

import sys
import os

# Allow import from packages/sdk-python when run from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../packages/sdk-python"))

from faccp_sdk.events.envelope import EventEnvelope


# ── Construction ──────────────────────────────────────────────────────────────

def test_envelope_creates_with_required_fields():
    agg_id = uuid.uuid4()
    env = EventEnvelope(
        event_type="order.created.v1",
        aggregate_id=agg_id,
        aggregate_version=1,
        producer="order-service",
    )
    assert env.event_type == "order.created.v1"
    assert env.aggregate_id == agg_id
    assert env.aggregate_version == 1
    assert env.producer == "order-service"
    assert env.schema_version == "1.0"


def test_envelope_auto_generates_ids():
    env1 = EventEnvelope(
        event_type="order.created.v1",
        aggregate_id=uuid.uuid4(),
        aggregate_version=1,
        producer="order-service",
    )
    env2 = EventEnvelope(
        event_type="order.created.v1",
        aggregate_id=uuid.uuid4(),
        aggregate_version=1,
        producer="order-service",
    )
    # Each envelope should have a unique event_id
    assert env1.event_id != env2.event_id


def test_envelope_occurred_at_is_utc():
    env = EventEnvelope(
        event_type="order.created.v1",
        aggregate_id=uuid.uuid4(),
        aggregate_version=1,
        producer="order-service",
    )
    assert env.occurred_at.tzinfo == timezone.utc


def test_envelope_is_immutable():
    env = EventEnvelope(
        event_type="order.created.v1",
        aggregate_id=uuid.uuid4(),
        aggregate_version=1,
        producer="order-service",
    )
    with pytest.raises(Exception):
        env.event_type = "order.cancelled.v1"  # type: ignore[misc]


# ── Validation: event_type format ─────────────────────────────────────────────

@pytest.mark.parametrize("valid_event_type", [
    "order.created.v1",
    "payment.captured.v1",
    "compliance.violation.v2",
    "delivery.completed.v1",
    "identity.authenticated.v1",
])
def test_event_type_valid_formats(valid_event_type: str):
    env = EventEnvelope(
        event_type=valid_event_type,
        aggregate_id=uuid.uuid4(),
        aggregate_version=1,
        producer="test-service",
    )
    assert env.event_type == valid_event_type


@pytest.mark.parametrize("invalid_event_type", [
    "order.created",          # missing version
    "order",                  # only one segment
    "order.created.latest",   # version not vN format
    "order.created.1",        # version doesn't start with v
    "",                       # empty
])
def test_event_type_invalid_formats_raise(invalid_event_type: str):
    with pytest.raises(ValidationError):
        EventEnvelope(
            event_type=invalid_event_type,
            aggregate_id=uuid.uuid4(),
            aggregate_version=1,
            producer="test-service",
        )


# ── Validation: schema_version ────────────────────────────────────────────────

@pytest.mark.parametrize("valid_schema", ["1.0", "2.0", "1.1", "10.5"])
def test_schema_version_valid(valid_schema: str):
    env = EventEnvelope(
        event_type="order.created.v1",
        aggregate_id=uuid.uuid4(),
        aggregate_version=1,
        producer="order-service",
        schema_version=valid_schema,
    )
    assert env.schema_version == valid_schema


@pytest.mark.parametrize("invalid_schema", ["1", "v1.0", "1.0.0", "abc", ""])
def test_schema_version_invalid_raises(invalid_schema: str):
    with pytest.raises(ValidationError):
        EventEnvelope(
            event_type="order.created.v1",
            aggregate_id=uuid.uuid4(),
            aggregate_version=1,
            producer="order-service",
            schema_version=invalid_schema,
        )


# ── Serialization ─────────────────────────────────────────────────────────────

def test_to_kafka_value_is_json_serializable():
    import json
    env = EventEnvelope(
        event_type="order.created.v1",
        aggregate_id=uuid.uuid4(),
        aggregate_version=1,
        producer="order-service",
        payload={"order_id": "ord_001", "amount": "700.00"},
    )
    kafka_val = env.to_kafka_value()
    # Should not raise
    serialized = json.dumps(kafka_val)
    assert "order.created.v1" in serialized
    assert "order-service" in serialized


def test_to_kafka_value_contains_all_required_fields():
    env = EventEnvelope(
        event_type="order.created.v1",
        aggregate_id=uuid.uuid4(),
        aggregate_version=1,
        producer="order-service",
    )
    val = env.to_kafka_value()
    required_fields = {
        "event_id", "event_type", "schema_version",
        "aggregate_id", "aggregate_version",
        "correlation_id", "causation_id",
        "producer", "occurred_at", "payload",
    }
    assert required_fields == set(val.keys())


def test_to_kafka_headers():
    env = EventEnvelope(
        event_type="order.created.v1",
        aggregate_id=uuid.uuid4(),
        aggregate_version=1,
        producer="order-service",
    )
    headers = env.to_kafka_headers()
    header_keys = {k for k, _ in headers}
    assert "event_type" in header_keys
    assert "correlation_id" in header_keys
    assert "producer" in header_keys


def test_round_trip_from_kafka_value():
    original = EventEnvelope(
        event_type="order.created.v1",
        aggregate_id=uuid.uuid4(),
        aggregate_version=1,
        producer="order-service",
        payload={"order_id": "ord_001"},
    )
    kafka_val = original.to_kafka_value()
    restored = EventEnvelope.from_kafka_value(kafka_val)
    assert restored.event_id == original.event_id
    assert restored.correlation_id == original.correlation_id
    assert restored.causation_id == original.causation_id
    assert restored.payload == original.payload


# ── Idempotency contract ──────────────────────────────────────────────────────

def test_same_event_id_can_be_detected_as_duplicate():
    """Consumers should use event_id to detect and skip duplicate processing."""
    shared_event_id = uuid.uuid4()
    agg_id = uuid.uuid4()

    env1 = EventEnvelope(
        event_id=shared_event_id,
        event_type="payment.captured.v1",
        aggregate_id=agg_id,
        aggregate_version=2,
        producer="payment-service",
    )
    env2 = EventEnvelope(
        event_id=shared_event_id,
        event_type="payment.captured.v1",
        aggregate_id=agg_id,
        aggregate_version=2,
        producer="payment-service",
    )
    # Duplicate detection: same event_id means same event
    assert env1.event_id == env2.event_id


def test_causal_chain_correlation():
    """Verify causation_id links parent event to child event."""
    parent = EventEnvelope(
        event_type="order.created.v1",
        aggregate_id=uuid.uuid4(),
        aggregate_version=1,
        producer="order-service",
    )
    child = EventEnvelope(
        event_type="payment.initiated.v1",
        aggregate_id=uuid.uuid4(),
        aggregate_version=1,
        producer="payment-service",
        causation_id=parent.event_id,
        correlation_id=parent.correlation_id,
    )
    assert child.causation_id == parent.event_id
    assert child.correlation_id == parent.correlation_id
