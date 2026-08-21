"""Authentication and identity endpoints for DrunkIt v0.1."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.middleware import get_current_request_id
from app.db.session import get_sync_db
from app.db.uow import SyncUnitOfWork
from app.models.identity import User
from app.schemas.auth import (
    LogoutResponse,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.identity_service import IdentityService

router = APIRouter(prefix="/auth", tags=["auth"])


def _format_user_response(user: User) -> UserResponse:
    """Format User model into UserResponse schema."""
    roles = [r.code for r in user.roles]
    return UserResponse(
        id=user.id,
        email=user.email,
        phone=user.phone,
        status=user.status,
        roles=roles,
        consumer_profile=user.consumer_profile,  # type: ignore[arg-type]
        created_at=user.created_at,
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register(
    request: UserRegisterRequest,
    session: Session = Depends(get_sync_db),
) -> UserResponse:
    """Create a new user account with assigned role (CONSUMER, RETAILER, BRAND, ADMIN)."""
    req_id = get_current_request_id()
    uow = SyncUnitOfWork(session)

    with uow:
        user = IdentityService.register_user(
            request=request,
            uow=uow,
            correlation_id=None,
        )

    # Reload user to ensure profile and roles are available
    fresh_user = IdentityService.get_user_by_id(user.id, session) or user
    return _format_user_response(fresh_user)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate and receive JWT access token",
)
def login(
    request: UserLoginRequest,
    session: Session = Depends(get_sync_db),
) -> TokenResponse:
    """Authenticate via email/phone and password to obtain a JWT bearer token."""
    uow = SyncUnitOfWork(session)

    with uow:
        user, token, expires_in = IdentityService.authenticate_user(
            request=request,
            uow=uow,
        )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        user=_format_user_response(user),
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Terminate active session",
)
def logout(current_user: User = Depends(get_current_user)) -> LogoutResponse:
    """Terminate the current authenticated session."""
    return LogoutResponse(status="ok", message=f"Session for user {current_user.id} terminated.")


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Retrieve the principal profile and assigned roles of the currently authenticated user."""
    return _format_user_response(current_user)
