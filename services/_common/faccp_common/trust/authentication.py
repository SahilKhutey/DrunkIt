"""Authentication: token creation, validation, and pipeline."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from faccp_common.trust.identity import (
    ActorType, AuthenticatedContext, Identity,
)


# ============================================================
# TOKEN STANDARDS
# ============================================================
ACCESS_TOKEN_LIFETIME = timedelta(minutes=15)
REFRESH_TOKEN_LIFETIME = timedelta(days=7)
ID_TOKEN_LIFETIME = timedelta(minutes=15)
SERVICE_TOKEN_LIFETIME = timedelta(minutes=5)

JWT_ALGORITHM = "HS256"
JWT_ISSUER = "faccp-platform"
JWT_AUDIENCE = "faccp-api"


# ============================================================
# TOKEN CREATION
# ============================================================
def create_access_token(
    identity: Identity,
    *,
    jwt_secret: str,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> tuple[str, str]:
    """Create a signed JWT access token. Returns (token, jti)."""
    now = datetime.now(timezone.utc)
    expires_at = now + (expires_delta or ACCESS_TOKEN_LIFETIME)
    jti = secrets.token_urlsafe(16)
    payload = {
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "sub": identity.actor_id,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": jti,
        "type": "access",
        "actor_type": identity.actor_type.value,
        "primary_role": identity.roles[0] if identity.roles else "CONSUMER",
        "roles": identity.roles,
        "organization_id": identity.organization_id,
        "assigned_stores": identity.assigned_stores,
        "assigned_jurisdictions": identity.assigned_jurisdictions,
        "consumer_level": identity.consumer_level,
        "seller_level": identity.seller_level,
        "mfa_enabled": identity.mfa_enabled,
        "trust_score": identity.trust_score,
        "tenant_id": identity.tenant_id,
    }
    if extra_claims:
        payload.update(extra_claims)
    token = jwt.encode(payload, jwt_secret, algorithm=JWT_ALGORITHM)
    return token, jti


def create_refresh_token(
    identity: Identity,
    *,
    jwt_secret: str,
    token_family_id: str | None = None,
) -> tuple[str, str, str]:
    """Create a refresh token. Returns (token, jti, family_id)."""
    now = datetime.now(timezone.utc)
    expires_at = now + REFRESH_TOKEN_LIFETIME
    jti = secrets.token_urlsafe(16)
    family_id = token_family_id or secrets.token_urlsafe(16)
    payload = {
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "sub": identity.actor_id,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": jti,
        "type": "refresh",
        "token_family_id": family_id,
    }
    token = jwt.encode(payload, jwt_secret, algorithm=JWT_ALGORITHM)
    return token, jti, family_id


def create_service_token(
    service_name: str,
    environment: str,
    instance_id: str,
    *,
    jwt_secret: str,
) -> str:
    """Create a short-lived service-to-service token."""
    now = datetime.now(timezone.utc)
    expires_at = now + SERVICE_TOKEN_LIFETIME
    payload = {
        "iss": JWT_ISSUER,
        "aud": "faccp-internal",
        "sub": f"service:{service_name}",
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": secrets.token_urlsafe(16),
        "type": "service",
        "service_name": service_name,
        "environment": environment,
        "instance_id": instance_id,
    }
    return jwt.encode(payload, jwt_secret, algorithm=JWT_ALGORITHM)


# ============================================================
# TOKEN VALIDATION
# ============================================================
@dataclass
class TokenValidationResult:
    valid: bool
    claims: dict[str, Any] = None
    error: str | None = None
    error_code: str | None = None


class TokenValidator:
    def __init__(self, jwt_secret: str) -> None:
        self._jwt_secret = jwt_secret

    def validate_access_token(self, token: str) -> TokenValidationResult:
        try:
            claims = jwt.decode(
                token,
                self._jwt_secret,
                algorithms=[JWT_ALGORITHM],
                issuer=JWT_ISSUER,
                audience=JWT_AUDIENCE,
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
            if claims.get("type") != "access":
                return TokenValidationResult(False, error_code="INVALID_TOKEN_TYPE")
            return TokenValidationResult(True, claims=claims)
        except JWTError as e:
            error_code = "TOKEN_EXPIRED" if "expired" in str(e).lower() else "INVALID_TOKEN"
            return TokenValidationResult(False, error=str(e), error_code=error_code)

    def validate_refresh_token(self, token: str) -> TokenValidationResult:
        try:
            claims = jwt.decode(
                token,
                self._jwt_secret,
                algorithms=[JWT_ALGORITHM],
                issuer=JWT_ISSUER,
                audience=JWT_AUDIENCE,
                options={"verify_exp": True, "require": ["exp", "iat", "sub", "jti", "type"]},
            )
            if claims.get("type") != "refresh":
                return TokenValidationResult(False, error_code="INVALID_TOKEN_TYPE")
            return TokenValidationResult(True, claims=claims)
        except JWTError as e:
            return TokenValidationResult(False, error=str(e), error_code="INVALID_REFRESH_TOKEN")

    def validate_service_token(self, token: str) -> TokenValidationResult:
        try:
            claims = jwt.decode(
                token,
                self._jwt_secret,
                algorithms=[JWT_ALGORITHM],
                issuer=JWT_ISSUER,
                audience="faccp-internal",
                options={"verify_exp": True, "require": ["exp", "sub", "jti", "type"]},
            )
            if claims.get("type") != "service":
                return TokenValidationResult(False, error_code="INVALID_TOKEN_TYPE")
            return TokenValidationResult(True, claims=claims)
        except JWTError as e:
            return TokenValidationResult(False, error=str(e), error_code="INVALID_SERVICE_TOKEN")


# ============================================================
# PASSWORD HASHING
# ============================================================
def hash_password(password: str) -> str:
    """Hash a password using argon2."""
    from passlib.context import CryptContext
    pwd_context = CryptContext(
        schemes=["argon2", "bcrypt"],
        deprecated="auto",
        argon2__memory_cost=65536,
        argon2__time_cost=3,
        argon2__parallelism=4,
    )
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


def generate_otp(length: int = 6) -> str:
    """Generate a numeric OTP."""
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


def hash_token(token: str) -> str:
    """Hash a token for storage (one-way)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# ============================================================
# AUTHENTICATION PIPELINE
# ============================================================
class AuthenticationPipeline:
    """Full authentication pipeline used by every protected route."""

    def __init__(self, token_validator: TokenValidator) -> None:
        self._validator = token_validator

    async def authenticate(
        self,
        token: str,
        session_lookup: callable = None,
    ) -> AuthenticatedContext | None:
        result = self._validator.validate_access_token(token)
        if not result.valid:
            return None
        claims = result.claims
        identity = Identity(
            actor_id=claims["sub"],
            actor_type=ActorType(claims.get("actor_type", "CONSUMER")),
            primary_identifier=claims.get("sub", ""),
            display_name=claims.get("sub", ""),
            roles=claims.get("roles", []),
            status="active",
            mfa_enabled=claims.get("mfa_enabled", False),
            trust_score=claims.get("trust_score", 50),
            organization_id=claims.get("organization_id"),
            assigned_stores=claims.get("assigned_stores", []),
            assigned_jurisdictions=claims.get("assigned_jurisdictions", []),
            consumer_level=claims.get("consumer_level"),
            seller_level=claims.get("seller_level"),
            tenant_id=claims.get("tenant_id"),
        )
        return AuthenticatedContext(
            identity=identity,
            claims=claims,
            mfa_verified=claims.get("mfa_enabled", False),
        )
