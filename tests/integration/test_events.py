"""Integration test for event envelope serialization and deserialization."""

from uuid import uuid4
from faccp_platform.events.envelope import EventEnvelope, EventMetadata
from faccp_platform.events.serialization import deserialize_event, serialize_event


def test_event_serialization():
    event = EventEnvelope(
        event_type="order.created",
        metadata=EventMetadata(
            producer="order-service",
            tenant_id="tenant-001",
            actor_id="user-123",
        ),
        payload={
            "order_id": str(uuid4()),
            "total": 1000,
        },
    )
    encoded = serialize_event(event)
    assert isinstance(encoded, bytes)

    decoded = deserialize_event(encoded)
    assert decoded.event_type == "order.created"
    assert decoded.event_id == event.event_id
    assert decoded.metadata.producer == "order-service"
    assert decoded.metadata.tenant_id == "tenant-001"
    assert decoded.payload["total"] == 1000
