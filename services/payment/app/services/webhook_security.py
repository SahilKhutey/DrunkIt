"""Webhook signature verification security module."""

from __future__ import annotations

import hashlib
import hmac


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify HMAC SHA-256 webhook signature against payload and secret."""
    if not signature or not secret:
        return False
    expected = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
