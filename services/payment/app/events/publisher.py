from datetime import datetime, timezone


class PaymentEventPublisher:

    def __init__(self, producer=None):
        self.producer = producer

    async def publish(
        self,
        event_name: str,
        payment: dict,
    ):
        if self.producer:
            await self.producer.publish(
                topic=event_name,
                key=str(payment.get("id")),
                value={
                    "event": event_name,
                    "payment_id": str(payment.get("id")),
                    "order_id": str(payment.get("order_id")),
                    "amount": payment.get("amount"),
                    "status": payment.get("status"),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
