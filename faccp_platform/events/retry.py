"""Exponential backoff retry policy implementation."""

from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


class RetryPolicy:
    """Exponential backoff retry policy with optional jitter."""

    def __init__(
        self,
        max_attempts: int = 5,
        base_delay: float | None = None,
        base_delay_seconds: float = 1.0,
        max_delay: float | None = None,
        max_delay_seconds: float = 300.0,
    ) -> None:
        self.max_attempts = max_attempts
        self.base_delay_seconds = base_delay if base_delay is not None else base_delay_seconds
        self.base_delay = self.base_delay_seconds
        self.max_delay_seconds = max_delay if max_delay is not None else max_delay_seconds
        self.max_delay = self.max_delay_seconds

    def delay(self, attempt: int) -> float:
        """Calculate exponential delay for attempt number."""
        exp_delay = self.base_delay_seconds * (2 ** (attempt - 1 if attempt > 0 else 0))
        return min(exp_delay, self.max_delay_seconds)

    def delay_with_jitter(self, attempt: int) -> float:
        """Calculate exponential delay with random jitter (0.8x to 1.2x)."""
        d = self.delay(attempt)
        return d * random.uniform(0.8, 1.2)

    async def execute(self, operation: Callable[[], Awaitable[T]]) -> T:
        """Execute async operation with retry backoff."""
        last_error: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                return await operation()
            except Exception as exc:
                last_error = exc
                if attempt == self.max_attempts:
                    break
                d = self.delay(attempt)
                await asyncio.sleep(d)
        raise last_error or RuntimeError("Operation failed with unknown error")
