"""FastAPI dependency for authenticating JWT Bearer tokens and yielding Principal."""

from __future__ import annotations

import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .principal import Principal
from .tokens import TokenService

bearer = HTTPBearer(auto_error=False)
token_service = TokenService()


async def get_current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> Principal:
    """Extract and validate Bearer token, returning the authenticated Principal."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    try:
        payload = token_service.decode_access_token(credentials.credentials)
        user_id = uuid.UUID(payload["sub"])
        roles = frozenset(payload.get("roles", []))
        permissions = frozenset(payload.get("permissions", []))
        tenant_id = payload.get("tenant_id")
        return Principal(
            user_id=user_id,
            roles=roles,
            permissions=permissions,
            tenant_id=tenant_id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        ) from exc
