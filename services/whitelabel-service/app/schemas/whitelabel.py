"""Whitelabel service API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TenantBrandingCreate(BaseModel):
    tenant_id: str
    brand_name: str = Field(min_length=2, max_length=128)
    logo_url: str | None = None
    primary_color_hex: str = Field(default="#1a202c", pattern="^#[0-9a-fA-F]{6}$")
    secondary_color_hex: str = Field(default="#319795", pattern="^#[0-9a-fA-F]{6}$")


class TenantBrandingResponse(BaseModel):
    id: str
    tenant_id: str
    brand_name: str
    logo_url: str | None
    primary_color_hex: str
    secondary_color_hex: str
    updated_at: datetime


class DomainBindingCreate(BaseModel):
    tenant_id: str
    domain_name: str = Field(min_length=3, max_length=255)


class DomainBindingResponse(BaseModel):
    id: str
    tenant_id: str
    domain_name: str
    ssl_certified: bool
    status: str
    created_at: datetime
