"""Eligibility decision database audit model."""

from __future__ import annotations

import json
from datetime import datetime
from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..domain.enums import DecisionStatus


class EligibilityDecisionModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Audit log model preserving full eligibility decision trace."""

    __tablename__ = "eligibility_decisions"

    consumer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    jurisdiction_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    policy_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status: Mapped[DecisionStatus] = mapped_column(
        Enum(DecisionStatus, name="eligibility_status"),
        nullable=False,
    )
    reasons_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    evaluated_rules_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    context_snapshot_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    engine_version: Mapped[str] = mapped_column(String(50), default="0.1.0", nullable=False)
