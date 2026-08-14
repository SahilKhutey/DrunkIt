"""Circuit Breaker pattern implementation."""

from __future__ import annotations

import time
from enum import Enum


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker pattern implementation protecting downstream services."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = CircuitState.CLOSED
        self.opened_at: float | None = None

    def allow_request(self) -> bool:
        """Check if request is permitted under current circuit state."""
        now = time.time()
        if self.state == CircuitState.OPEN:
            if self.opened_at is not None and (now - self.opened_at) >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        return True

    def record_success(self) -> None:
        """Record successful call, resetting circuit to CLOSED."""
        self.failures = 0
        self.state = CircuitState.CLOSED
        self.opened_at = None

    def record_failure(self) -> None:
        """Record failed call, opening circuit if threshold exceeded."""
        self.failures += 1
        if self.failures >= self.failure_threshold or self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.opened_at = time.time()
