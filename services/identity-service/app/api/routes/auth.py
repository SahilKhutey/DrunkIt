"""Authentication API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.dto import SuccessResponse
from faccp_common.exceptions import BadRequestError, NotFoundError, UnauthorizedError

from app.api.dependencies import get_auth_service, get_current_user, to_authenticated_context
from app.db.models import User
from app.schemas.auth import (
    LoginRequest, LogoutRequest, MFASetupResponse, MFAVerifyRequest,
    PasswordChangeRequest, PasswordResetConfirm, PasswordResetRequest,
    RegisterRequest, SessionResponse, TokenResponse, UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _client_info(request: Request) -> tuple[str, str]:
    return (
        request.client.host if request.client else "0.0.0.0",
        request.headers.get("user-agent", "unknown"),
    )


@router.post("/register", response_model=SuccessResponse[TokenResponse], status_code=201)
async def register(
    payload: RegisterRequest,
    request: Request,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[TokenResponse]:
    ip, ua = _client_info(request)
    tokens = await service.register(
        payload, ip_address=ip, user_agent=ua,
        device_fingerprint=payload.device_fingerprint,
        device_name=payload.device_name,
    )
    return SuccessResponse(data=tokens, message="Registration successful")


@router.post("/login", response_model=SuccessResponse[TokenResponse])
async def login(
    payload: LoginRequest,
    request: Request,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[TokenResponse]:
    ip, ua = _client_info(request)
    tokens = await service.login(payload, ip_address=ip, user_agent=ua)
    return SuccessResponse(data=tokens, message="Login successful")


@router.post("/refresh", response_model=SuccessResponse[TokenResponse])
async def refresh(
    payload: dict,
    request: Request,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[TokenResponse]:
    from app.schemas.auth import RefreshRequest
    refresh_payload = RefreshRequest(**payload)
    ip, ua = _client_info(request)
    tokens = await service.refresh_tokens(
        refresh_payload.refresh_token, ip_address=ip, user_agent=ua,
    )
    return SuccessResponse(data=tokens, message="Token refreshed")


@router.post("/logout", response_model=SuccessResponse[None])
async def logout(
    payload: LogoutRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[None]:
    await service.logout(user.id, payload.refresh_token, payload.all_devices)
    return SuccessResponse(data=None, message="Logged out")


@router.post("/password/change", response_model=SuccessResponse[None])
async def change_password(
    payload: PasswordChangeRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[None]:
    await service.change_password(user.id, payload)
    return SuccessResponse(data=None, message="Password changed")


@router.post("/password/reset/request", response_model=SuccessResponse[None])
async def request_password_reset(
    payload: PasswordResetRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[None]:
    await service.request_password_reset(payload)
    return SuccessResponse(
        data=None, message="If the email exists, a reset link has been sent.",
    )


@router.post("/password/reset/confirm", response_model=SuccessResponse[None])
async def confirm_password_reset(
    payload: PasswordResetConfirm,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[None]:
    await service.confirm_password_reset(payload)
    return SuccessResponse(data=None, message="Password reset successful")


@router.post("/mfa/setup", response_model=SuccessResponse[MFASetupResponse])
async def mfa_setup(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[MFASetupResponse]:
    result = await service.setup_mfa(user.id)
    return SuccessResponse(data=result, message="Scan QR and verify to enable MFA")


@router.post("/mfa/verify", response_model=SuccessResponse[None])
async def mfa_verify_setup(
    payload: MFAVerifyRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[None]:
    ok = await service.verify_mfa_setup(user.id, payload)
    if not ok:
        raise BadRequestError("Invalid MFA code")
    return SuccessResponse(data=None, message="MFA enabled successfully")


@router.post("/mfa/disable", response_model=SuccessResponse[None])
async def mfa_disable(
    payload: dict,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[None]:
    password = payload.get("current_password")
    if not password:
        raise BadRequestError("current_password is required")
    await service.disable_mfa(user.id, password)
    return SuccessResponse(data=None, message="MFA disabled")


@router.get("/me", response_model=SuccessResponse[UserResponse])
async def get_me(
    user: Annotated[User, Depends(get_current_user)],
) -> SuccessResponse[UserResponse]:
    return SuccessResponse(data=UserResponse(
        id=user.id, email=user.email, phone=user.phone,
        email_verified=user.email_verified, phone_verified=user.phone_verified,
        is_active=user.is_active, primary_role=user.primary_role, roles=user.roles,
        mfa_enabled=user.mfa_enabled, mfa_method=user.mfa_method,
        organization_id=user.organization_id, assigned_stores=user.assigned_stores,
        assigned_jurisdictions=user.assigned_jurisdictions,
        consumer_id=user.consumer_id, retailer_id=user.retailer_id, driver_id=user.driver_id,
        consumer_level=user.consumer_level, seller_level=user.seller_level,
        created_at=user.created_at, last_login_at=user.last_login_at,
    ))


@router.get("/sessions", response_model=SuccessResponse[list[SessionResponse]])
async def list_sessions(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[list[SessionResponse]]:
    sessions = await service.list_sessions(user.id)
    return SuccessResponse(data=[SessionResponse(
        id=s.id, ip_address=s.ip_address, user_agent=s.user_agent,
        device_id=s.device_id, geo_country=s.geo_country,
        is_active=s.is_active, created_at=s.created_at,
        expires_at=s.expires_at, last_used_at=s.last_used_at,
    ) for s in sessions])
