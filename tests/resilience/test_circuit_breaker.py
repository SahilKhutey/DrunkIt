"""Unit tests for Circuit Breaker state machine transitions."""

import time
import pytest
from faccp_platform.resilience.circuit_breaker import CircuitBreaker, CircuitState


def test_circuit_breaker_transitions():
    """Verify circuit transitions CLOSED -> OPEN after 3 failures -> HALF_OPEN after recovery timeout -> CLOSED on success."""
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.2)
    assert cb.state == CircuitState.CLOSED
    assert cb.allow_request() is True

    # Record 2 failures -> remains CLOSED
    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED

    # 3rd failure -> opens circuit
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.allow_request() is False

    # Wait for recovery timeout -> transitions to HALF_OPEN
    time.sleep(0.25)
    assert cb.allow_request() is True
    assert cb.state == CircuitState.HALF_OPEN

    # Success in HALF_OPEN resets to CLOSED
    cb.record_success()
    assert cb.state == CircuitState.CLOSED
    assert cb.failures == 0
