"""Sliding window token bucket rate limiting module."""

from __future__ import annotations

import time
from collections import defaultdict


class SlidingWindowRateLimiter:
    """In-memory sliding window rate limiter."""

    def __init__(self, limit: int = 60, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._history: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds
        
        # Clean expired timestamps
        self._history[key] = [t for t in self._history[key] if t > cutoff]

        if len(self._history[key]) < self.limit:
            self._history[key].append(now)
            return True
        return False

    def remaining_tokens(self, key: str) -> int:
        now = time.time()
        cutoff = now - self.window_seconds
        valid_requests = [t for t in self._history[key] if t > cutoff]
        return max(0, self.limit - len(valid_requests))
