from datetime import datetime, timezone


class OrderEventPublisher:

    def __init__(self, producer=None):
        self.producer = producer

    async def publish(
        self,
        event_name: str,
        order: dict,
    ):
        if self.producer:
            await self.producer.publish(
                topic=event_name,
                key=str(order.get("id")),
                value={
                    "event": event_name,
                    "order_id": str(order.get("id")),
                    "customer_id": str(order.get("customer_id")),
                    "store_id": str(order.get("store_id")),
                    "status": order.get("status"),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
