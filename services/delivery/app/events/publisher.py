from datetime import datetime, timezone


class DeliveryEventPublisher:

    def __init__(self, producer=None):
        self.producer = producer

    async def publish(self, event_name: str, delivery: dict):
        if self.producer:
            await self.producer.publish(
                topic=event_name,
                key=str(delivery.get("id")),
                value={
                    "event": event_name,
                    "delivery_id": str(delivery.get("id")),
                    "order_id": str(delivery.get("order_id")),
                    "status": delivery.get("status"),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
