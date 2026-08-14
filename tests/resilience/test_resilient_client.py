"""Unit tests for ResilientClient combining Timeout, Circuit Breaker, and Bulkhead."""

import asyncio
import pytest
from faccp_platform.resilience.bulkhead import Bulkhead
from faccp_platform.resilience.circuit_breaker import CircuitBreaker, CircuitState
from faccp_platform.resilience.client import ResilientClient


@pytest.mark.asyncio
async def test_resilient_client_timeout():
    """Verify operation exceeding timeout raises TimeoutError."""
    client = ResilientClient(timeout=0.1)

    async def slow_operation():
        await asyncio.sleep(0.3)
        return "ok"

    with pytest.raises(TimeoutError, match="Operation exceeded 0.1s limit"):
        await client.execute(slow_operation)


@pytest.mark.asyncio
async def test_resilient_client_circuit_open_blocking():
    """Verify that repeated failures open circuit breaker and block subsequent requests."""
    breaker = CircuitBreaker(failure_threshold=2)
    client = ResilientClient(timeout=1.0, breaker=breaker)

    async def failing_op():
        raise ValueError("Provider down")

    with pytest.raises(ValueError):
        await client.execute(failing_op)

    with pytest.raises(ValueError):
        await client.execute(failing_op)

    # Circuit is now open
    assert breaker.state == CircuitState.OPEN

    with pytest.raises(RuntimeError, match="Circuit is open"):
        await client.execute(failing_op)
