import json

from packages.cache.keys import RedisKey
from packages.cache.redis import redis


class IdempotencyService:

    async def get(
        self,
        key: str,
    ):

        value = await redis.get(
            RedisKey.idempotency(key)
        )

        if value is None:
            return None

        return json.loads(value)

    async def save(
        self,
        key: str,
        response: dict,
        ttl: int = 86400,
    ):

        await redis.set(
            RedisKey.idempotency(key),
            json.dumps(response),
            ex=ttl,
        )
