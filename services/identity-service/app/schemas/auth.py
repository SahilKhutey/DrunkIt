"""Authentication API schemas."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    phone: str | None = Field(default=None, min_length=10, max_length=15)
    password: str = Field(min_length=12, max_length=128)
    primary_role: Literal["CONSUMER", "RETAILER_OWNER"] = "CONSUMER"
    device_fingerprint: str | None = None
    device_name: str | None = None
    locale: str = Field(default="en-IN", min_length=2, max_length=10)
    timezone: str = Field(default="Asia/Kolkata", max_length=64)
    consent: dict[str, bool] = Field(default_factory=dict)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain a lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain a digit")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", v):
            raise ValueError("Password must contain a special character")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_fingerprint: str | None = None
    device_name: str | None = None
    mfa_code: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user_id: str
    email: str
    roles: list[str]
    primary_role: str
    mfa_required: bool = False
    mfa_verified: bool = False


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str | None = None
    all_devices: bool = False


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=12, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain a lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain a digit")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", v):
            raise ValueError("Password must contain a special character")
        return v


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=12, max_length=128)


class MFASetupResponse(BaseModel):
    secret: str
    qr_code_url: str
    backup_codes: list[str]


class MFAVerifyRequest(BaseModel):
    code: str = Field(min_length=6, max_length=8)


class UserResponse(BaseModel):
    id: str
    email: str
    phone: str | None
    email_verified: bool
    phone_verified: bool
    is_active: bool
    primary_role: str
    roles: list[str]
    mfa_enabled: bool
    mfa_method: str | None
    organization_id: str | None
    assigned_stores: list[str]
    assigned_jurisdictions: list[str]
    consumer_id: str | None
    retailer_id: str | None
    driver_id: str | None
    consumer_level: str | None
    seller_level: str | None
    created_at: datetime
    last_login_at: datetime | None


class SessionResponse(BaseModel):
    id: str
    ip_address: str
    user_agent: str
    device_id: str | None
    geo_country: str | None
    is_active: bool
    created_at: datetime
    expires_at: datetime
    last_used_at: datetime
    is_current: bool = False
