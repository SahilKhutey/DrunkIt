import asyncio


class Bulkhead:

    def __init__(self, capacity: int = 20):
        self.capacity = capacity
        self.semaphore = asyncio.Semaphore(capacity)

    async def execute(self, operation_coro_fn):
        async with self.semaphore:
            return await operation_coro_fn()
