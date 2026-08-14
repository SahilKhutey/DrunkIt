"""Identity request and response schemas."""

from __future__ import annotations

import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12)
    first_name: str | None = None
    last_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str | None = None
    last_name: str | None = None
    status: str
    email_verified: bool

    model_config = ConfigDict(from_attributes=True)
