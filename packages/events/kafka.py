import json

from aiokafka import AIOKafkaProducer


class KafkaEventProducer:

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
    ):

        self.producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda value:
                json.dumps(value).encode(),
        )

    async def start(self):

        await self.producer.start()

    async def stop(self):

        await self.producer.stop()

    async def publish(
        self,
        topic: str,
        event: dict,
    ):

        await self.producer.send_and_wait(
            topic,
            event,
        )
