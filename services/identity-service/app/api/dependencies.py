"""FastAPI dependencies: DB, services, current user."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated, Any

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.database import get_db
from faccp_common.exceptions import ForbiddenError, UnauthorizedError
from faccp_common.trust.authentication import TokenValidator
from faccp_common.trust.identity import ActorType, AuthenticatedContext, Identity

from app.config import get_settings
from app.db.models import User
from app.services.auth_service import AuthService

settings = get_settings()


async def get_event_producer(request: Request):
    producer = getattr(request.app.state, "event_producer", None)
    if producer is None:
        raise HTTPException(status_code=503, detail="Event producer unavailable")
    return producer


def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    return get_db()


def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    producer = Depends(get_event_producer),
) -> AuthService:
    return AuthService(db=db, producer=producer)


def get_token_validator() -> TokenValidator:
    return TokenValidator(settings.jwt_secret)


async def get_current_user(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
    validator: TokenValidator = Depends(get_token_validator),
) -> User:
    """Extract and validate the current user from JWT."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1].strip()
    result = validator.validate_access_token(token)
    if not result.valid:
        raise UnauthorizedError(result.error or "Invalid token", details={"code": result.error_code})
    user_id = result.claims["sub"]
    db_gen = get_db_session()
    db = await anext(db_gen.__aiter__())
    try:
        from sqlalchemy import select
        db_result = await db.execute(select(User).where(User.id == user_id))
        user = db_result.scalar_one_or_none()
        if not user:
            raise UnauthorizedError("User not found")
        if not user.is_active:
            raise UnauthorizedError("User is not active")
        if user.is_locked:
            raise ForbiddenError("User is locked")
        request.state.current_user = user
        request.state.jwt_claims = result.claims
        return user
    finally:
        try:
            await db_gen.__anext__()
        except StopAsyncIteration:
            pass


def require_roles(*allowed_roles: str):
    async def checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        if not user.has_any_role(list(allowed_roles)):
            raise ForbiddenError(
                f"Required role: {' or '.join(allowed_roles)}",
                details={"required_roles": list(allowed_roles), "user_roles": user.roles},
            )
        return user
    return checker


def to_authenticated_context(user: User, claims: dict) -> AuthenticatedContext:
    identity = Identity(
        actor_id=user.id, actor_type=ActorType(user.primary_role if user.primary_role in ActorType._value2member_map_ else "CONSUMER"),
        primary_identifier=user.email, display_name=user.email,
        roles=user.roles or [user.primary_role],
        status="active" if user.is_active and not user.is_locked else "suspended",
        mfa_enabled=user.mfa_enabled, trust_score=user.trust_score,
        organization_id=user.organization_id,
        assigned_stores=user.assigned_stores,
        assigned_jurisdictions=user.assigned_jurisdictions,
        consumer_level=user.consumer_level,
        seller_level=user.seller_level,
    )
    return AuthenticatedContext(identity=identity, claims=claims,
                                mfa_verified=claims.get("mfa_enabled", False))
