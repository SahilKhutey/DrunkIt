"""Dead Letter Queue (DLQ) publisher for failed events."""

from __future__ import annotations

from .envelope import EventEnvelope
from .producer import EventProducer
from .topics import Topics


class DeadLetterPublisher:
    """Redirects unprocessable/poison messages to the DLQ topic."""

    def __init__(self, producer: EventProducer) -> None:
        self.producer = producer

    async def publish(
        self,
        event: EventEnvelope,
        *,
        source_topic: str,
        error: str,
    ) -> None:
        dlq_payload = {
            **event.payload,
            "_dlq": {
                "source_topic": source_topic,
                "error": error,
            },
        }
        dlq_event = event.model_copy(update={"payload": dlq_payload})
        await self.producer.publish(Topics.DEAD_LETTER, dlq_event)
