"""Contract schema validation tests using jsonschema."""

import json
import os
import pytest
from jsonschema import validate
from faccp_platform.events.envelope import create_event
from faccp_platform.events.versioning import validate_version, UnsupportedEventVersion


def load_schema(rel_path: str) -> dict:
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    schema_file = os.path.join(root_dir, "contracts", "events", rel_path)
    with open(schema_file, "r", encoding="utf-8") as f:
        return json.load(f)


def test_event_envelope_schema_validation():
    """Verify EventEnvelope JSON serialization passes common envelope schema."""
    envelope_schema = load_schema("common/event-envelope.json")
    event = create_event(
        event_type="order.created",
        producer="order-service",
        aggregate_type="order",
        aggregate_id="11111111-1111-1111-1111-111111111111",
        correlation_id="22222222-2222-2222-2222-222222222222",
        payload={"order_id": "ord_123"},
    )
    raw = event.to_flat_dict()
    validate(instance=raw, schema=envelope_schema)


def test_order_created_schema_validation():
    """Verify OrderCreated payload passes order-created.v1.json schema."""
    order_schema = load_schema("order/order-created.v1.json")
    payload = {
        "order_id": "ord_123",
        "customer_id": "cust_456",
        "currency": "INR",
        "total_amount": 499.0,
        "items": [{"product_id": "P001", "quantity": 2}],
    }
    validate(instance=payload, schema=order_schema)


def test_unsupported_event_version_rejection():
    """Verify unsupported schema version raises UnsupportedEventVersion exception."""
    assert validate_version("order.created", 1) is True
    with pytest.raises(UnsupportedEventVersion):
        validate_version("order.created", 99)
