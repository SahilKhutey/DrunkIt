from datetime import datetime, timezone
from uuid import uuid4

from packages.events.contracts import (
    EventEnvelope,
)


def create_event(
    event_type: str,
    aggregate_type: str,
    aggregate_id: str,
    payload: dict,
) -> EventEnvelope:

    return EventEnvelope(

        event_id=uuid4(),

        event_type=event_type,

        aggregate_type=aggregate_type,

        aggregate_id=aggregate_id,

        occurred_at=datetime.now(
            timezone.utc
        ),

        payload=payload,
    )
