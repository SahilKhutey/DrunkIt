from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.database import get_db
from faccp_common.dto import APIResponse
from identity_app.api.dependencies import get_current_account
from identity_app.db.models import Account
from identity_app.schemas.auth import (
    LoginRequest,
    MFAEnableResponse,
    MFAVerifyRequest,
    RegisterRequest,
    TokenResponse,
    UserProfileResponse,
)
from identity_app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    req: RegisterRequest, db: Annotated[AsyncSession, Depends(get_db)]
) -> APIResponse[dict[str, str]]:
    svc = AuthService(db)
    account = await svc.register(req)
    return APIResponse(
        data={"user_id": account.id, "email": account.email, "message": "Account created successfully."}
    )


@router.post("/login")
async def login(
    req: LoginRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_agent: str | None = Header(None),
) -> APIResponse[TokenResponse]:
    svc = AuthService(db)
    tokens = await svc.login(req, user_agent=user_agent, ip_address=request.client.host if request.client else None)
    return APIResponse(data=tokens)


@router.get("/me")
async def get_profile(
    current_account: Annotated[Account, Depends(get_current_account)]
) -> APIResponse[UserProfileResponse]:
    return APIResponse(
        data=UserProfileResponse(
            id=current_account.id,
            email=current_account.email,
            email_verified=current_account.email_verified,
            phone_verified=current_account.phone_verified,
            account_type=current_account.account_type.value,
            status=current_account.status.value,
            mfa_enabled=current_account.mfa_enabled,
            roles=[r.name for r in current_account.roles],
            created_at=current_account.created_at,
        )
    )


@router.post("/mfa/setup")
async def setup_mfa(
    current_account: Annotated[Account, Depends(get_current_account)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> APIResponse[MFAEnableResponse]:
    svc = AuthService(db)
    resp = await svc.enable_mfa(current_account.id)
    return APIResponse(data=resp)


@router.post("/mfa/verify")
async def verify_mfa(
    req: MFAVerifyRequest,
    current_account: Annotated[Account, Depends(get_current_account)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> APIResponse[dict[str, str]]:
    svc = AuthService(db)
    await svc.verify_mfa_enable(current_account.id, req.code)
    return APIResponse(data={"message": "MFA enabled successfully."})
