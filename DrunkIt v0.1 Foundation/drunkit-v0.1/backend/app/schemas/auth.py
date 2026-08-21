"""Pydantic schemas for identity, user authentication, and RBAC contracts."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ConsumerProfileResponse(BaseModel):
    """Consumer profile data response."""

    preferred_market: str | None = None
    date_of_birth_verified: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    """User account representation in API responses."""

    id: uuid.UUID
    email: str | None = None
    phone: str | None = None
    status: str
    roles: list[str] = Field(default_factory=list)
    consumer_profile: ConsumerProfileResponse | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserRegisterRequest(BaseModel):
    """Request payload for user registration."""

    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=10, max_length=20)
    password: str = Field(min_length=8, max_length=128, description="Plaintext password")
    role: str = Field(default="CONSUMER", description="Target role: CONSUMER, RETAILER, BRAND, ADMIN")
    preferred_market: str | None = Field(default=None, description="Preferred state code (e.g. IN-WB)")


class UserLoginRequest(BaseModel):
    """Request payload for password-based authentication."""

    email: str | None = None
    phone: str | None = None
    password: str = Field(min_length=1, description="Plaintext password")


class TokenResponse(BaseModel):
    """Authentication token response with principal information."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class LogoutResponse(BaseModel):
    """Response returned upon session termination."""

    status: str = "ok"
    message: str = "Session successfully terminated."
