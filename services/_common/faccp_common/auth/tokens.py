"""
JWT Token Standards & Token Extractor (§15.1, §15.2).
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
import jwt

from ..exceptions import InvalidAuthHeaderError, InvalidTokenError, MissingAuthError, TokenExpiredError

JWT_SECRET_DEFAULT = "faccp_platform_jwt_secret_key_32bytes_minimum!"


class TokenStandards:
    ACCESS_TOKEN_LIFETIME_SECONDS = 900  # 15 minutes
    REFRESH_TOKEN_LIFETIME_SECONDS = 604800  # 7 days
    ACCESS_TOKEN_ALGORITHM = "HS256"
    ACCESS_TOKEN_TYPE = "access"
    REFRESH_TOKEN_TYPE = "refresh"
    JWT_ISSUER = "faccp-platform"
    JWT_AUDIENCE = "faccp-api"


def get_jwt_secret() -> str:
    return os.getenv("JWT_SECRET_KEY", JWT_SECRET_DEFAULT)


def create_access_token(
    user_id: str,
    roles: list[str],
    primary_role: str,
    *,
    permissions: list[str] | None = None,
    organization_id: str | None = None,
    assigned_stores: list[str] | None = None,
    assigned_jurisdictions: list[str] | None = None,
    consumer_level: str | None = None,
    seller_level: str | None = None,
    mfa_verified: bool = False,
    trust_score: int = 50,
    tenant_id: str | None = None,
    device_id: str | None = None,
    session_id: str | None = None,
    secret_key: str | None = None,
) -> tuple[str, str]:
    """Create a signed JWT access token. Returns (token, jti)."""
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())
    secret = secret_key or get_jwt_secret()

    payload = {
        "iss": TokenStandards.JWT_ISSUER,
        "aud": TokenStandards.JWT_AUDIENCE,
        "sub": user_id,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=TokenStandards.ACCESS_TOKEN_LIFETIME_SECONDS)).timestamp()),
        "jti": jti,
        "type": TokenStandards.ACCESS_TOKEN_TYPE,
        "roles": roles,
        "primary_role": primary_role,
        "permissions": permissions or [],
        "organization_id": organization_id,
        "assigned_stores": assigned_stores or [],
        "assigned_jurisdictions": assigned_jurisdictions or [],
        "consumer_level": consumer_level,
        "seller_level": seller_level,
        "mfa_verified": mfa_verified,
        "mfa_timestamp": int(now.timestamp()) if mfa_verified else None,
        "trust_score": trust_score,
        "tenant_id": tenant_id,
        "device_id": device_id,
        "session_id": session_id,
    }

    token = jwt.encode(payload, secret, algorithm=TokenStandards.ACCESS_TOKEN_ALGORITHM)
    return token, jti


def validate_access_token(token: str, secret_key: str | None = None) -> dict[str, Any]:
    """Validate JWT access token. Raises on signature or claim failure."""
    secret = secret_key or get_jwt_secret()
    try:
        claims = jwt.decode(
            token,
            secret,
            algorithms=[TokenStandards.ACCESS_TOKEN_ALGORITHM],
            issuer=TokenStandards.JWT_ISSUER,
            audience=TokenStandards.JWT_AUDIENCE,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
                "verify_iss": True,
                "verify_aud": True,
                "require": ["iss", "aud", "sub", "iat", "nbf", "exp", "jti", "type"],
            },
        )
        if claims.get("type") != TokenStandards.ACCESS_TOKEN_TYPE:
            raise InvalidTokenError(f"Invalid token type: {claims.get('type')}")
        return claims
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Access token has expired")
    except jwt.PyJWTError as e:
        raise InvalidTokenError(f"Invalid token: {e}")


class TokenExtractor:
    HEADER_NAME = "Authorization"
    SCHEME = "Bearer"

    @staticmethod
    def extract_from_header(auth_header: str | None) -> str:
        if not auth_header:
            raise MissingAuthError("Authorization header required")
        parts = auth_header.split(" ", 1)
        if len(parts) != 2:
            raise InvalidAuthHeaderError("Authorization header must be 'Bearer <token>'")
        scheme, token = parts
        if scheme.lower() != TokenExtractor.SCHEME.lower():
            raise InvalidAuthHeaderError(f"Authorization scheme must be '{TokenExtractor.SCHEME}'")
        if not token or len(token) < 20:
            raise InvalidTokenError("Token is empty or too short")
        return token.strip()
