from packages.events.outbox import (
    OutboxEvent,
)


async def enqueue_event(
    session,
    event,
):

    record = OutboxEvent(

        id=event.event_id,

        event_type=event.event_type,

        aggregate_type=(
            event.aggregate_type
        ),

        aggregate_id=event.aggregate_id,

        payload=event.model_dump(
            mode="json"
        ),

        created_at=event.occurred_at,
    )

    session.add(record)
