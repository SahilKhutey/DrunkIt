"""Reliability patterns: retry, circuit breaker, idempotency."""

from __future__ import annotations

import asyncio
import functools
import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class RetryPolicy:
    """Exponential backoff with jitter."""

    max_attempts: int = 4
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    jitter_factor: float = 0.25  # ±25% randomness

    @classmethod
    def get_delay(cls, attempt: int = 0) -> float:
        policy = cls()
        delay = min(
            policy.base_delay_seconds * (5 ** attempt),
            policy.max_delay_seconds,
        )
        jitter = delay * policy.jitter_factor * (random.random() * 2 - 1)
        return max(0.0, delay + jitter)


def with_retry(
    retry_policy: RetryPolicy | None = None,
    retry_on: tuple[type[BaseException], ...] = (Exception,),
):
    """Decorator: retry async function with exponential backoff."""
    policy = retry_policy or RetryPolicy()

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exc: BaseException | None = None
            for attempt in range(policy.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except retry_on as e:
                    last_exc = e
                    if attempt < policy.max_attempts - 1:
                        delay = policy.get_delay(attempt)
                        logger.warning(
                            "retry.attempt_failed",
                            extra={
                                "func": func.__name__,
                                "attempt": attempt + 1,
                                "delay": delay,
                                "error": str(e),
                            },
                        )
                        await asyncio.sleep(delay)
            raise last_exc  # type: ignore[misc]
        return wrapper
    return decorator


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitOpenError(Exception):
    pass


@dataclass
class CircuitBreaker:
    """Circuit breaker: CLOSED -> OPEN -> HALF_OPEN -> CLOSED/OPEN."""

    failure_threshold: int = 5
    recovery_timeout_seconds: float = 30.0
    half_open_max_calls: int = 3
    success_threshold_to_close: int = 2

    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: float | None = None
    half_open_calls: int = 0
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def call(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self.last_failure_time and (
                    time.time() - self.last_failure_time
                ) >= self.recovery_timeout_seconds:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                    logger.info("circuit.half_open")
                else:
                    raise CircuitOpenError("Circuit OPEN, retry later")
            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls >= self.half_open_max_calls:
                    raise CircuitOpenError("Circuit HALF_OPEN at max calls")
                self.half_open_calls += 1

        try:
            result = await func(*args, **kwargs)
        except Exception:
            async with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.OPEN
                    logger.warning("circuit.reopened")
                elif self.failure_count >= self.failure_threshold:
                    self.state = CircuitState.OPEN
                    logger.warning("circuit.opened", extra={"failures": self.failure_count})
            raise

        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold_to_close:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    logger.info("circuit.closed")
            else:
                self.failure_count = 0
        return result


def with_circuit_breaker(circuit_breaker: CircuitBreaker):
    """Decorator: wrap async function with circuit breaker."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            return await circuit_breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator
