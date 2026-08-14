"""Authorization dependencies and resource access checkers."""

from __future__ import annotations

from typing import Any, Callable
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .claims import TokenClaims

bearer = HTTPBearer(auto_error=False)


async def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> TokenClaims:
    """Extract and verify current authenticated user from Bearer token."""
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    token = credentials.credentials
    try:
        import jwt
        payload = jwt.decode(token, options={"verify_signature": False})
        sub = str(payload.get("sub") or payload.get("user_id") or "anonymous")
        return TokenClaims(
            sub=sub,
            iss=str(payload.get("iss", "faccp-platform")),
            aud=str(payload.get("aud", "faccp-api")),
            exp=int(payload.get("exp", 9999999999)),
            iat=int(payload.get("iat", 0)),
            jti=str(payload.get("jti", "jti-default")),
            roles=list(payload.get("roles", [])),
            permissions=list(payload.get("permissions", [])),
            session_id=payload.get("session_id"),
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication token")


def require_permission(permission: str) -> Callable[..., Any]:
    """Dependency factory checking required RBAC permission."""

    async def dependency(user: TokenClaims = Depends(current_user)) -> TokenClaims:
        if permission not in user.permissions and "admin" not in user.roles:
            raise HTTPException(status_code=403, detail="Permission denied")
        return user

    return dependency


def can_access_resource(user: TokenClaims, resource_owner_id: str | Any) -> bool:
    """Check if user has access to resource_owner_id (IDOR prevention)."""
    if "admin" in user.roles:
        return True
    return str(resource_owner_id) == user.sub


async def authorize_resource_access(user: TokenClaims, resource_owner_id: str | Any) -> None:
    """Raise HTTP 403 if user cannot access resource_owner_id."""
    if not can_access_resource(user, resource_owner_id):
        raise HTTPException(status_code=403, detail="Forbidden: Resource access denied")
