import pytest
from services.resilience.app.engine.circuit_breaker import CircuitBreaker, call_with_breaker
from services.resilience.app.models.enums import CircuitState


@pytest.mark.asyncio
async def test_circuit_breaker_trip():
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1.0)
    assert breaker.state == CircuitState.CLOSED

    async def fail_fn():
        raise RuntimeError("SERVICE_DOWN")

    with pytest.raises(RuntimeError):
        await call_with_breaker(breaker, fail_fn)

    with pytest.raises(RuntimeError):
        await call_with_breaker(breaker, fail_fn)

    assert breaker.state == CircuitState.OPEN

    with pytest.raises(RuntimeError, match="CIRCUIT_OPEN"):
        await call_with_breaker(breaker, fail_fn)
