"""Platform database models registered with Base metadata."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDPrimaryKeyMixin


# Phase 5 Legacy Platform Models
class UserAccountModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "faccp_user_accounts"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="CONSUMER", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class TenantModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "faccp_tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)


class AuditLogModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "faccp_audit_logs"

    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    actor_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    prev_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    curr_hash: Mapped[str] = mapped_column(String(64), nullable=False)


class OutboxEventModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "faccp_outbox_events"

    event_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(100), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(100), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)


# Association Tables
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", String(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", String(36), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


# Phase 4 Security Kernel Models
class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """User account entity."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", index=True, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    roles: Mapped[list[Role]] = relationship("Role", secondary=user_roles, lazy="selectin")


class Role(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """RBAC Role entity."""

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    permissions: Mapped[list[Permission]] = relationship("Permission", secondary=role_permissions, lazy="selectin")


class Permission(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """RBAC Permission entity."""

    __tablename__ = "permissions"

    resource: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(100), index=True, nullable=False)


class RefreshToken(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Hashed Refresh Tokens entity."""

    __tablename__ = "refresh_tokens"

    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class AuditLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Audit log entry entity."""

    __tablename__ = "audit_logs"

    action: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    actor_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    resource_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)


class ProcessedEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Tracks processed events to guarantee idempotent message handling."""

    __tablename__ = "processed_events"

    event_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    consumer: Mapped[str] = mapped_column(String(100), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class EventOutbox(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Transactional Outbox table for atomic event publishing."""

    __tablename__ = "event_outbox"

    event_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


try:
    from faccp_platform.saga.models import SagaInstance  # noqa: F401
    from faccp_platform.security.idempotency import IdempotencyRecord  # noqa: F401
    from faccp_platform.verification.models import VerificationRecord  # noqa: F401
except ImportError:
    pass

