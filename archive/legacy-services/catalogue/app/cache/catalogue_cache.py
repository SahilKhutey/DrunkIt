class CatalogueCache:

    def __init__(self, redis_client=None):
        self.redis = redis_client

    async def get_listing(self, listing_id: str):
        if self.redis:
            return await self.redis.get(f"listing:{listing_id}")
        return None

    async def set_listing(self, listing_id: str, value: str, ttl: int = 300):
        if self.redis:
            await self.redis.set(f"listing:{listing_id}", value, ex=ttl)
