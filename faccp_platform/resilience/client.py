"""Resilient client wrapper combining Timeout, Circuit Breaker, and Bulkhead isolation."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypeVar
from .bulkhead import Bulkhead
from .circuit_breaker import CircuitBreaker
from .timeout import with_timeout

T = TypeVar("T")


class ResilientClient:
    """Production client combining Circuit Breaker, Bulkhead, and Timeout controls."""

    def __init__(
        self,
        timeout: float = 5.0,
        breaker: CircuitBreaker | None = None,
        bulkhead: Bulkhead | None = None,
    ) -> None:
        self.timeout = timeout
        self.breaker = breaker or CircuitBreaker()
        self.bulkhead = bulkhead or Bulkhead()

    async def execute(self, operation: Callable[[], Awaitable[T]]) -> T:
        """Execute operation protected by circuit state check, bulkhead concurrency, and timeout limits."""
        if not self.breaker.allow_request():
            raise RuntimeError("Circuit is open")

        async def run() -> T:
            return await with_timeout(operation, self.timeout)

        try:
            result = await self.bulkhead.execute(run)
            self.breaker.record_success()
            return result
        except Exception as exc:
            self.breaker.record_failure()
            raise exc
