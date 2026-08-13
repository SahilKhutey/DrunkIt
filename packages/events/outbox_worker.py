import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from packages.database.session import (
    SessionFactory,
)
from packages.events.kafka import (
    KafkaEventProducer,
)
from packages.events.outbox import (
    OutboxEvent,
)

TOPIC = "platform.events"


class OutboxWorker:

    def __init__(self, bootstrap_servers: str = "localhost:9092"):

        self.producer = KafkaEventProducer(
            bootstrap_servers=bootstrap_servers
        )

    async def run(self):

        await self.producer.start()

        try:

            while True:

                await self.process_batch()

                await asyncio.sleep(0.5)

        finally:

            await self.producer.stop()

    async def process_batch(self):

        async with SessionFactory() as session:

            result = await session.execute(
                select(OutboxEvent)
                .where(OutboxEvent.published_at == None)
                .order_by(OutboxEvent.created_at)
                .limit(100)
            )

            events = result.scalars().all()

            for event in events:

                try:

                    await self.producer.publish(
                        TOPIC,
                        event.payload,
                    )

                    event.published_at = datetime.now(
                        timezone.utc
                    )

                except Exception as exc:

                    event.error = str(exc)

            await session.commit()
