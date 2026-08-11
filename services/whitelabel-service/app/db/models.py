"""White-label service — multi-tenant theming, branding, and configuration."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin
from app.db.base import Base


class Tenant(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "tenants"

    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    legal_name: Mapped[str] = mapped_column(String(256), nullable=False)
    primary_region: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    allowed_regions: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    data_residency: Mapped[str] = mapped_column(String(32), default="strict", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    subscription_tier: Mapped[str] = mapped_column(String(32), default="standard", nullable=False)
    feature_flags: Mapped[dict[str, bool]] = mapped_column(JSONB, default=dict, nullable=False)
    rate_limits: Mapped[dict[str, int]] = mapped_column(JSONB, default=dict, nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)


class TenantTheme(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "tenant_themes"

    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    favicon_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    brand_name: Mapped[str] = mapped_column(String(128), nullable=False)
    tagline: Mapped[str | None] = mapped_column(String(256), nullable=True)
    primary_color: Mapped[str] = mapped_column(String(7), default="#0066CC", nullable=False)
    secondary_color: Mapped[str] = mapped_column(String(7), default="#00AA88", nullable=False)
    accent_color: Mapped[str] = mapped_column(String(7), default="#FF6600", nullable=False)
    background_color: Mapped[str] = mapped_column(String(7), default="#FFFFFF", nullable=False)
    text_color: Mapped[str] = mapped_column(String(7), default="#1A1A1A", nullable=False)
    error_color: Mapped[str] = mapped_column(String(7), default="#CC0000", nullable=False)
    success_color: Mapped[str] = mapped_column(String(7), default="#00AA00", nullable=False)
    font_family: Mapped[str] = mapped_column(String(128), default="Inter, sans-serif", nullable=False)
    heading_font: Mapped[str] = mapped_column(String(128), default="Inter, sans-serif", nullable=False)
    border_radius: Mapped[str] = mapped_column(String(16), default="8px", nullable=False)
    custom_css: Mapped[str | None] = mapped_column(Text, nullable=True)
    email_header_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    email_footer_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    assets: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)


class CustomDomain(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "custom_domains"

    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_token: Mapped[str] = mapped_column(String(64), nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ssl_status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    ssl_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TenantConfig(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "tenant_configs"

    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    config_key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    config_value: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    __table_args__ = (
        Index("ix_tenant_config_key", "tenant_id", "config_key", unique=True),
    )
