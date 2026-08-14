"""JWT Token generation and verification service."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
import jwt

from faccp_platform.config.settings import get_settings


class TokenService:
    """JWT Token management service using PyJWT."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def create_access_token(
        self,
        *,
        user_id: str | uuid.UUID,
        roles: list[str] | None = None,
        permissions: list[str] | None = None,
        tenant_id: str | None = None,
    ) -> str:
        """Issue an access JWT token."""
        roles = roles or []
        permissions = permissions or []
        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=self.settings.access_token_expire_minutes)

        payload = {
            "sub": str(user_id),
            "type": "access",
            "roles": roles,
            "permissions": permissions,
            "tenant_id": tenant_id,
            "iat": now,
            "exp": expires,
            "jti": str(uuid.uuid4()),
        }

        return jwt.encode(
            payload,
            self.settings.access_token_secret,
            algorithm="HS256",
        )

    def decode_access_token(self, token: str) -> dict:
        """Decode and validate an access JWT token."""
        return jwt.decode(
            token,
            self.settings.access_token_secret,
            algorithms=["HS256"],
        )
