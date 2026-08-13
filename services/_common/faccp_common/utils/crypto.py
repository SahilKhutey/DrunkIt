"""Cryptographic and hashing helper utilities."""

from __future__ import annotations

import hashlib
import hmac
import secrets


def hash_sha256(data: str) -> str:
    """Calculates SHA256 hex digest for input string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def generate_secure_token(length: int = 32) -> str:
    """Generates cryptographically secure URL-safe token."""
    return secrets.token_urlsafe(length)


def compute_hmac_signature(secret_key: str, payload: str) -> str:
    """Computes HMAC-SHA256 signature for payload verification."""
    return hmac.new(
        secret_key.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
