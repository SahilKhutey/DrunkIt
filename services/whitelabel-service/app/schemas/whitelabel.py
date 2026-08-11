import re
from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator


class CreateTenantRequest(BaseModel):
    code: str = Field(min_length=3, max_length=31)
    name: str = Field(min_length=2, max_length=128)
    legal_name: str = Field(min_length=2, max_length=256)
    primary_region: str = Field(min_length=2, max_length=32)
    allowed_regions: list[str] = Field(default_factory=list)
    data_residency: Literal["strict", "flexible", "none"] = "strict"
    subscription_tier: Literal["starter", "standard", "enterprise", "custom"] = "standard"
    feature_flags: dict[str, bool] = Field(default_factory=dict)
    rate_limits: dict[str, int] = Field(default_factory=dict)
    contact_email: EmailStr
    contact_phone: str | None = None


class TenantResponse(BaseModel):
    id: str
    code: str
    name: str
    legal_name: str
    primary_region: str
    allowed_regions: list[str]
    is_active: bool
    subscription_tier: str
    feature_flags: dict[str, bool]
    created_at: datetime


class CreateThemeRequest(BaseModel):
    name: str = "default"
    is_default: bool = False
    logo_url: str | None = None
    favicon_url: str | None = None
    brand_name: str
    tagline: str | None = None
    primary_color: str = "#0066CC"
    secondary_color: str = "#00AA88"
    accent_color: str = "#FF6600"
    background_color: str = "#FFFFFF"
    text_color: str = "#1A1A1A"
    error_color: str = "#CC0000"
    success_color: str = "#00AA00"
    font_family: str = "Inter, sans-serif"
    heading_font: str = "Inter, sans-serif"
    border_radius: str = "8px"
    custom_css: str | None = None
    email_header_html: str | None = None
    email_footer_html: str | None = None
    assets: dict[str, Any] = Field(default_factory=dict)

    @field_validator("primary_color", "secondary_color", "accent_color", "background_color", "text_color", "error_color", "success_color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError("Color must be in #RRGGBB format")
        return v


class ThemeResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    is_default: bool
    brand_name: str
    tagline: str | None
    logo_url: str | None
    favicon_url: str | None
    primary_color: str
    secondary_color: str
    accent_color: str
    background_color: str
    text_color: str
    error_color: str
    success_color: str
    font_family: str
    border_radius: str
    custom_css: str | None


class CustomDomainRequest(BaseModel):
    domain: str


class CustomDomainResponse(BaseModel):
    id: str
    domain: str
    is_primary: bool
    verified: bool
    verification_token: str
    ssl_status: str
    verified_at: datetime | None


class VerifyDomainResponse(BaseModel):
    id: str
    domain: str
    verified: bool
    ssl_status: str


class TenantConfigRequest(BaseModel):
    key: str = Field(min_length=1, max_length=128)
    value: dict[str, Any]
    is_sensitive: bool = False
