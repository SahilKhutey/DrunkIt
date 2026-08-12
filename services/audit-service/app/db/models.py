"""Audit service database models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from faccp_common.models import UUIDPrimaryKeyMixin, utc_now

from app.db.base import Base


class CryptographicAuditEntry(UUIDPrimaryKeyMixin, Base):
    """Immutable hash-chained audit log entry."""

    __tablename__ = "cryptographic_audit_entries"

    sequence_number: Mapped[int] = mapped_column(Integer, primary_key=False, autoincrement=True, unique=True, index=True)
    event_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    actor_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    actor_role: Mapped[str] = mapped_column(String(32), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    resource_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    payload_json: Mapped[str] = mapped_column(Text, nullable=False)

    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    current_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
