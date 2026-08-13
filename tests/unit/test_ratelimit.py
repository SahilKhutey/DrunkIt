"""
Unit tests for Rate Limiting module.
"""

from __future__ import annotations

import time
import pytest
from faccp_common.ratelimit import SlidingWindowRateLimiter


def test_rate_limiter_allowed_within_limit():
    limiter = SlidingWindowRateLimiter(limit=5, window_seconds=60)
    client_key = "user_123"

    for _ in range(5):
        assert limiter.is_allowed(client_key) is True

    assert limiter.remaining_tokens(client_key) == 0
    assert limiter.is_allowed(client_key) is False
