"""JSON Event Envelope serialization and deserialization helpers."""

from __future__ import annotations

import json
from .envelope import EventEnvelope


def serialize_event(event: EventEnvelope) -> bytes:
    """Serialize an EventEnvelope instance to UTF-8 bytes."""
    return json.dumps(
        event.model_dump(mode="json"),
        separators=(",", ":"),
    ).encode("utf-8")


def deserialize_event(data: bytes) -> EventEnvelope:
    """Deserialize UTF-8 bytes to an EventEnvelope instance."""
    return EventEnvelope.model_validate(json.loads(data.decode("utf-8")))
