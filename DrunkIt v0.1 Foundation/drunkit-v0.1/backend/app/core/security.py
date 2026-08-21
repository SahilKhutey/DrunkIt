"""Security, password hashing, and JWT token management for DrunkIt v0.1."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.exceptions import UnauthorizedError
from app.settings import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Compute a secure bcrypt hash of a plaintext password."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def create_access_token(
    subject: str | uuid.UUID,
    roles: list[str],
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Generate a signed JWT access token for an authenticated principal."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload: dict[str, Any] = {
        "sub": str(subject),
        "roles": roles,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": "drunkit-api",
    }
    if extra_claims:
        payload.update(extra_claims)

    encoded_jwt = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a signed JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            issuer="drunkit-api",
            options={"require": ["exp", "sub", "iat"]},
        )
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedError(
            message="Access token has expired. Please authenticate again.",
            code="TOKEN_EXPIRED",
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedError(
            message="Invalid or malformed authentication token.",
            code="INVALID_TOKEN",
        ) from exc
