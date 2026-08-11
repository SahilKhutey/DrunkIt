from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    account_type: str = "CONSUMER"
    phone: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    mfa_code: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    roles: list[str]


class RefreshRequest(BaseModel):
    refresh_token: str


class MFAEnableResponse(BaseModel):
    secret: str
    otpauth_url: str
    qr_code_base64: str


class MFAVerifyRequest(BaseModel):
    code: str


class UserProfileResponse(BaseModel):
    id: str
    email: str
    email_verified: bool
    phone_verified: bool
    account_type: str
    status: str
    mfa_enabled: bool
    roles: list[str]
    created_at: datetime
