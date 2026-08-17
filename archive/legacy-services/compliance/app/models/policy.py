"""Compliance Policy database model."""

from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..domain.enums import PolicyStatus


class CompliancePolicy(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Regulated commerce policy entity model."""

    __tablename__ = "compliance_policies"

    jurisdiction_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)
    status: Mapped[PolicyStatus] = mapped_column(
        Enum(PolicyStatus, name="compliance_policy_status"),
        default=PolicyStatus.DRAFT,
        nullable=False,
    )
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
