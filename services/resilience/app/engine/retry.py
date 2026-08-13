import asyncio
import random
from dataclasses import dataclass
from functools import wraps


@dataclass
class RetryPolicy:

    max_attempts: int = 3

    base_delay: float = 0.25

    max_delay: float = 5.0

    multiplier: float = 2.0


def backoff_delay(attempt: int, policy: RetryPolicy) -> float:
    delay = policy.base_delay * (policy.multiplier**attempt)
    return min(delay, policy.max_delay)


def jittered_delay(attempt: int, policy: RetryPolicy) -> float:
    delay = backoff_delay(attempt, policy)
    return random.uniform(delay * 0.8, delay * 1.2)


def retry(policy: RetryPolicy | None = None, exceptions=(Exception,)):
    pol = policy or RetryPolicy()

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(pol.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions:
                    last_attempt = attempt == pol.max_attempts - 1
                    if last_attempt:
                        raise
                    await asyncio.sleep(jittered_delay(attempt, pol))

        return wrapper

    return decorator


async def with_timeout(operation_coro_fn, timeout_seconds: float):
    return await asyncio.wait_for(operation_coro_fn(), timeout=timeout_seconds)
