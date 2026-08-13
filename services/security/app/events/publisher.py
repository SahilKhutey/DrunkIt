from datetime import datetime, timezone


class SecurityEventPublisher:

    def __init__(self, producer=None):
        self.producer = producer

    async def publish(self, event_name: str, payload: dict):
        if self.producer:
            await self.producer.publish(
                topic=event_name,
                key=str(payload.get("subject_id", "security")),
                value={
                    "event": event_name,
                    "payload": payload,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
