from __future__ import annotations

from typing import Any

import redis.asyncio as redis


class RedisClient:
    """Async Redis client wrapper."""

    def __init__(self, url: str, max_connections: int = 50) -> None:
        self._url = url
        self._max_connections = max_connections
        self._client: redis.Redis | None = None

    async def connect(self) -> None:
        self._client = redis.from_url(
            self._url,
            max_connections=self._max_connections,
            decode_responses=True,
            health_check_interval=30,
        )
        await self._client.ping()

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()
            self._client = None

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            raise RuntimeError("Redis not connected.")
        return self._client

    async def get(self, key: str) -> Any:
        return await self.client.get(key)

    async def set(self, key: str, value: Any, ex: int | None = None) -> None:
        await self.client.set(key, value, ex=ex)

    async def delete(self, *keys: str) -> int:
        return await self.client.delete(*keys)

    async def exists(self, key: str) -> bool:
        return bool(await self.client.exists(key))

    async def expire(self, key: str, seconds: int) -> bool:
        return bool(await self.client.expire(key, seconds))
