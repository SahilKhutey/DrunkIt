import time
from services.resilience.app.models.enums import CircuitState


class CircuitBreaker:

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.opened_at: float | None = None

    def can_execute(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if self.opened_at and (time.monotonic() - self.opened_at) >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False

        return True

    def record_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.opened_at = time.monotonic()


async def call_with_breaker(breaker: CircuitBreaker, operation_coro_fn):
    if not breaker.can_execute():
        raise RuntimeError("CIRCUIT_OPEN")

    try:
        res = await operation_coro_fn()
        breaker.record_success()
        return res
    except Exception:
        breaker.record_failure()
        raise
