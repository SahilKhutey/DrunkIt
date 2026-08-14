"""Bulkhead isolation pattern implementation."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


class Bulkhead:
    """Bulkhead concurrency isolation pattern implementation."""

    def __init__(self, max_concurrent: int = 20) -> None:
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def execute(self, operation: Callable[[], Awaitable[T]]) -> T:
        """Execute operation within semaphore concurrency bounds."""
        async with self.semaphore:
            return await operation()
