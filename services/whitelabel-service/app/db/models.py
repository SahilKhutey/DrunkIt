"""Whitelabel service database models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin, utc_now

from app.db.base import Base


class TenantBrandingConfig(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Custom tenant UI theme and branding configuration."""

    __tablename__ = "tenant_branding_configs"

    tenant_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    brand_name: Mapped[str] = mapped_column(String(128), nullable=False)
    logo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    primary_color_hex: Mapped[str] = mapped_column(String(7), default="#1a202c", nullable=False)
    secondary_color_hex: Mapped[str] = mapped_column(String(7), default="#319795", nullable=False)


class CustomDomainBinding(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Custom CNAME domain mapping for enterprise retailers."""

    __tablename__ = "custom_domain_bindings"

    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    domain_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    ssl_certified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)
