"""
IP-based rate limiting via slowapi, plus a couple of dedicated, tighter
limits on the auth endpoints — those are the ones with a real abuse
cost (SMS spend per OTP request; brute-force risk on verify).

This handles "one IP hitting us too fast." It does NOT by itself stop
someone spraying OTP requests at one victim's phone number from many
different IPs — that's handled separately by the per-phone cooldown
in app/domain/auth/service.py, which is IP-independent.
"""
from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings

settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120/minute"],
    enabled=settings.rate_limit_enabled,
)
