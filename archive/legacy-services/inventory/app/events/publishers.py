class InventoryEventPublisher:

    def __init__(self, producer=None):
        self.producer = producer

    async def publish(
        self,
        event_name: str,
        entity_id: str,
        payload: dict,
    ):
        if self.producer:
            await self.producer.publish(
                topic=event_name,
                key=str(entity_id),
                value={
                    "event": event_name,
                    "entity_id": str(entity_id),
                    "payload": payload,
                },
            )
