class VelocityEngine:

    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.in_memory_counters: dict[str, int] = {}

    async def increment(self, key: str, window_seconds: int = 60) -> int:
        if self.redis:
            count = await self.redis.incr(key)
            if count == 1:
                await self.redis.expire(key, window_seconds)
            return count

        # In-memory fallback
        count = self.in_memory_counters.get(key, 0) + 1
        self.in_memory_counters[key] = count
        return count

    async def check_order_velocity(self, consumer_id: str) -> dict | None:
        key = f"risk:orders:{consumer_id}:60"
        count = await self.increment(key, 60)
        if count >= 10:
            return {"signal_type": "ORDER_VELOCITY", "score": 50.0, "severity": "HIGH"}
        if count >= 5:
            return {"signal_type": "ORDER_VELOCITY", "score": 20.0, "severity": "MEDIUM"}
        return None

    async def check_verification_velocity(self, consumer_id: str) -> dict | None:
        key = f"risk:verification:{consumer_id}:300"
        count = await self.increment(key, 300)
        if count >= 8:
            return {"signal_type": "VERIFICATION_ABUSE", "score": 60.0, "severity": "HIGH"}
        return None

    async def check_payment_velocity(self, consumer_id: str) -> dict | None:
        key = f"risk:payment:{consumer_id}:600"
        count = await self.increment(key, 600)
        if count >= 10:
            return {"signal_type": "PAYMENT_VELOCITY", "score": 40.0, "severity": "HIGH"}
        return None
