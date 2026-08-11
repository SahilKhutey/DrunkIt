"""Audit service models — append-only event store with hash chaining."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from faccp_common.models import UUIDPrimaryKeyMixin, utc_now
from app.db.base import Base


class AuditEvent(UUIDPrimaryKeyMixin, Base):
    """An immutable audit event. Append-only — never updated or deleted."""
    __tablename__ = "audit_events"

    # Identity
    event_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    sequence_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)

    # WHO
    actor_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    actor_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # user|service|system
    actor_role: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    actor_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    actor_user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    organization_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)

    # WHAT
    action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    resource_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # RESULT
    result: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # success|failure|denied|review
    severity: Mapped[str] = mapped_column(String(16), default="info", nullable=False, index=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # CONTEXT
    service_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    causation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    policy_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    jurisdiction_code: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)

    # PAYLOAD
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    before_state: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    after_state: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # TIMING
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # CHAIN — links to previous event for tamper detection
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    event_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)

    __table_args__ = (
        Index("ix_audit_actor_action", "actor_id", "action"),
        Index("ix_audit_resource", "resource_type", "resource_id"),
        Index("ix_audit_time_actor", "occurred_at", "actor_id"),
        Index("ix_audit_service_time", "service_name", "occurred_at"),
    )


class AuditExport(UUIDPrimaryKeyMixin, Base):
    """Record of audit data exports — for accountability."""
    __tablename__ = "audit_exports"

    requested_by: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    requested_by_role: Mapped[str] = mapped_column(String(64), nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    filters: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    record_count: Mapped[int] = mapped_column(Integer, nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
