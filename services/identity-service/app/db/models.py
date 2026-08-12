"""Identity service database models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin, utc_now

from app.db.base import Base


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Core identity record. PII-light by design (email/phone for login; PII lives in consumer-service)."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True, index=True)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)

    primary_role: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    roles: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)

    organization_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    assigned_stores: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    assigned_jurisdictions: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )
    consumer_level: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    seller_level: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    trust_score: Mapped[int] = mapped_column(Integer, default=50, nullable=False, index=True)
    risk_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)

    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_method: Mapped[str | None] = mapped_column(String(32), nullable=True)
    mfa_secret_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    mfa_backup_codes_hashed: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )
    mfa_enrolled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    locale: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    consumer_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    retailer_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    driver_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)

    sessions: Mapped[list["Session"]] = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )
    devices: Mapped[list["Device"]] = relationship(
        "Device", back_populates="user", cascade="all, delete-orphan"
    )
    api_keys: Mapped[list["APIKey"]] = relationship(
        "APIKey", back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_users_role_active", "primary_role", "is_active"),
        Index("ix_users_org_role", "organization_id", "primary_role"),
    )

    def has_role(self, role: str) -> bool:
        return role == self.primary_role or role in (self.roles or [])

    def has_any_role(self, roles: list[str]) -> bool:
        return any(self.has_role(r) for r in roles)


class Session(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Server-side session. Absolute and idle timeouts enforced."""

    __tablename__ = "sessions"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    refresh_token_hash: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False, index=True
    )
    token_family_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    access_jti: Mapped[str | None] = mapped_column(String(64), nullable=True)

    ip_address: Mapped[str] = mapped_column(String(64), nullable=False)
    user_agent: Mapped[str] = mapped_column(Text, nullable=False)
    device_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)

    geo_country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    geo_state: Mapped[str | None] = mapped_column(String(64), nullable=True)
    geo_city: Mapped[str | None] = mapped_column(String(128), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    absolute_expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="sessions")


class Device(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Registered device for a user. Trust-scored."""

    __tablename__ = "devices"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    device_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    device_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    device_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    os: Mapped[str | None] = mapped_column(String(64), nullable=True)
    browser: Mapped[str | None] = mapped_column(String(64), nullable=True)

    is_trusted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    trust_score: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    last_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="devices")


class APIKey(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """API keys for service-to-service or developer access."""

    __tablename__ = "api_keys"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    organization_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    key_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    key_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    key_prefix: Mapped[str] = mapped_column(String(16), nullable=False)
    scopes: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="api_keys")


class RoleDefinition(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Persisted role definitions (mirrors the enum)."""

    __tablename__ = "role_definitions"

    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    domain: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    parent_roles: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )
    permissions: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )
    is_system: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class PasswordResetToken(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "password_reset_tokens"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )


class EmailVerificationToken(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "email_verification_tokens"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
