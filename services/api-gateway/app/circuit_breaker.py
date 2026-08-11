"""
Circuit Breaker pattern implementation for upstream service protection.
"""

from __future__ import annotations

import time
from enum import Enum
from typing import Callable, Any
from faccp_common.logging import get_logger

logger = get_logger(__name__)


class CircuitState(str, Enum):
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Failing — fast reject requests
    HALF_OPEN = "HALF_OPEN"# Testing recovery


class CircuitBreakerOpenException(Exception):
    def __init__(self, service_name: str, reset_in: float):
        super().__init__(f"Circuit breaker for {service_name} is OPEN. Try again in {reset_in:.1f}s")
        self.service_name = service_name
        self.reset_in = reset_in


class CircuitBreaker:

    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 5,
        recovery_time_seconds: float = 30.0,
        half_open_success_threshold: int = 2,
    ) -> None:
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_time_seconds = recovery_time_seconds
        self.half_open_success_threshold = half_open_success_threshold

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_state_change = time.monotonic()
        self.opened_at: float | None = None

    async def call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        now = time.monotonic()

        if self.state == CircuitState.OPEN:
            elapsed = now - (self.opened_at or now)
            if elapsed >= self.recovery_time_seconds:
                self._transition_to(CircuitState.HALF_OPEN)
            else:
                remaining = self.recovery_time_seconds - elapsed
                raise CircuitBreakerOpenException(self.service_name, remaining)

        try:
            res = await func(*args, **kwargs)
            self._on_success()
            return res
        except Exception as e:
            self._on_failure(e)
            raise

    def _on_success(self) -> None:
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_success_threshold:
                self._transition_to(CircuitState.CLOSED)
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def _on_failure(self, exc: Exception) -> None:
        self.failure_count += 1
        if self.state in (CircuitState.CLOSED, CircuitState.HALF_OPEN):
            if self.failure_count >= self.failure_threshold or self.state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.OPEN)

    def _transition_to(self, new_state: CircuitState) -> None:
        logger.info(
            "circuit_breaker.state_change",
            service=self.service_name,
            from_state=self.state.value,
            to_state=new_state.value,
        )
        self.state = new_state
        self.last_state_change = time.monotonic()
        if new_state == CircuitState.OPEN:
            self.opened_at = time.monotonic()
            self.failure_count = 0
        elif new_state == CircuitState.HALF_OPEN:
            self.success_count = 0
            self.failure_count = 0
        elif new_state == CircuitState.CLOSED:
            self.failure_count = 0
            self.success_count = 0
            self.opened_at = None
