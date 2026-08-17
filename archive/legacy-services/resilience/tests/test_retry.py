import pytest
from services.resilience.app.engine.retry import RetryPolicy, backoff_delay, jittered_delay, retry, with_timeout


def test_exponential_backoff_and_jitter():
    policy = RetryPolicy(max_attempts=3, base_delay=0.1, max_delay=1.0)
    delay0 = backoff_delay(0, policy)
    delay1 = backoff_delay(1, policy)

    assert delay0 == 0.1
    assert delay1 == 0.2
    assert 0.08 <= jittered_delay(0, policy) <= 0.12


@pytest.mark.asyncio
async def test_retry_decorator_success():
    attempts = 0

    @retry(RetryPolicy(max_attempts=3, base_delay=0.01))
    async def transient_fn():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise ValueError("TRANSIENT_ERROR")
        return "SUCCESS"

    res = await transient_fn()
    assert res == "SUCCESS"
    assert attempts == 2
