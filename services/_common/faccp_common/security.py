from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from jose import JWTError, jwt
import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against a hash."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False



def generate_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def generate_otp(length: int = 6) -> str:
    """Generate a numeric OTP."""
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


def hash_token(token: str) -> str:
    """Hash a token for storage (deterministic lookup)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_access_token(
    subject: str,
    *,
    secret: str,
    algorithm: str,
    issuer: str,
    audience: str,
    expires_minutes: int = 15,
    claims: dict[str, Any] | None = None,
) -> str:
    """Create a signed JWT access token."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iss": issuer,
        "aud": audience,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
        "jti": generate_token(16),
        "type": "access",
        **(claims or {}),
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


def create_refresh_token(
    subject: str,
    *,
    secret: str,
    algorithm: str,
    issuer: str,
    audience: str,
    expires_days: int = 7,
) -> str:
    """Create a signed JWT refresh token."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iss": issuer,
        "aud": audience,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int((now + timedelta(days=expires_days)).timestamp()),
        "jti": generate_token(16),
        "type": "refresh",
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_token(
    token: str,
    *,
    secret: str,
    algorithm: str,
    issuer: str,
    audience: str,
    expected_type: str | None = None,
) -> dict[str, Any]:
    """Decode and validate a JWT."""
    options = {"verify_aud": True}
    payload = jwt.decode(
        token,
        secret,
        algorithms=[algorithm],
        issuer=issuer,
        audience=audience,
        options=options,
    )
    if expected_type and payload.get("type") != expected_type:
        raise JWTError(f"Invalid token type: expected {expected_type}")
    return payload


class FieldEncryption:
    """Symmetric encryption for sensitive fields (Fernet/AES-128-CBC + HMAC)."""

    def __init__(self, key: str) -> None:
        try:
            self._fernet = Fernet(key.encode() if isinstance(key, str) else key)
        except (ValueError, TypeError):
            derived = base64.urlsafe_b64encode(
                hashlib.sha256(key.encode()).digest()
            )
            self._fernet = Fernet(derived)

    def encrypt(self, plaintext: str) -> str:
        if plaintext is None:
            return None  # type: ignore[return-value]
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        if ciphertext is None:
            return None  # type: ignore[return-value]
        try:
            return self._fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
        except InvalidToken as exc:
            raise ValueError("Invalid ciphertext") from exc


def constant_time_compare(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def pseudonymize(value: str, salt: str = "faccp") -> str:
    """Create a deterministic pseudonym for a value (HMAC-SHA256)."""
    return hmac.new(
        salt.encode("utf-8"), value.encode("utf-8"), hashlib.sha256
    ).hexdigest()
