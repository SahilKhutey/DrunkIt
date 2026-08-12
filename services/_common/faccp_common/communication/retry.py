"""
Retry Policy (Exponential Backoff with Jitter).
"""

from __future__ import annotations

import random


class RetryPolicy:
    MAX_ATTEMPTS = 4
    BASE_DELAY_SECONDS = 1.0
    MAX_DELAY_SECONDS = 60.0
    JITTER_FACTOR = 0.25

    @classmethod
    def get_delay(cls, attempt: int) -> float:
        delay = min(
            cls.BASE_DELAY_SECONDS * (5 ** attempt),
            cls.MAX_DELAY_SECONDS,
        )
        jitter = delay * cls.JITTER_FACTOR * (random.random() * 2 - 1)
        return max(0.0, delay + jitter)
