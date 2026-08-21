"""FastAPI dependency injection utilities for authentication, authorization, and RBAC guards."""

import uuid
from collections.abc import Callable
from typing import Any

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.db.session import get_sync_db
from app.models.identity import User
from app.services.identity_service import IdentityService

http_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer_scheme),
    session: Session = Depends(get_sync_db),
) -> User:
    """Extract and validate the authenticated user principal from Bearer token."""
    if not credentials or not credentials.credentials:
        raise UnauthorizedError(
            message="Authentication credentials were not provided.",
            code="AUTHENTICATION_REQUIRED",
        )

    payload = decode_access_token(credentials.credentials)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError("Token subject is missing.", code="INVALID_TOKEN")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError as exc:
        raise UnauthorizedError("Token subject is invalid.", code="INVALID_TOKEN") from exc

    user = IdentityService.get_user_by_id(user_id, session)
    if not user:
        raise UnauthorizedError("User account associated with this token was not found.", code="USER_NOT_FOUND")

    if user.status != "ACTIVE":
        raise ForbiddenError("User account is inactive.", code="ACCOUNT_INACTIVE")

    return user


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer_scheme),
    session: Session = Depends(get_sync_db),
) -> User | None:
    """Extract authenticated user if credentials exist, otherwise return None."""
    if not credentials or not credentials.credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None
        user_id = uuid.UUID(user_id_str)
        return IdentityService.get_user_by_id(user_id, session)
    except Exception:
        return None


def require_roles(*allowed_roles: str) -> Callable[[User], User]:
    """Dependency factory enforcing that the authenticated principal possesses at least one allowed role."""

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_roles = {role.code.upper() for role in current_user.roles}
        required_roles = {r.strip().upper() for r in allowed_roles}

        # Platform ADMIN role has universal bypass
        if "ADMIN" in user_roles or bool(user_roles & required_roles):
            return current_user

        raise ForbiddenError(
            message=f"Access denied. Requires one of roles: {', '.join(allowed_roles)}.",
            code="INSUFFICIENT_PERMISSIONS",
            details={
                "required_roles": list(allowed_roles),
                "user_roles": list(user_roles),
            },
        )

    return role_checker
