import json

from aiokafka import AIOKafkaConsumer


class KafkaEventConsumer:

    def __init__(
        self,
        topic: str,
        group_id: str,
        bootstrap_servers: str = "localhost:9092",
    ):

        self.consumer = AIOKafkaConsumer(

            topic,

            bootstrap_servers=bootstrap_servers,

            group_id=group_id,

            value_deserializer=(
                lambda value:
                json.loads(
                    value.decode()
                )
            ),
        )

    async def start(self):

        await self.consumer.start()

    async def stop(self):

        await self.consumer.stop()

    async def messages(self):

        async for message in self.consumer:

            yield message.value
