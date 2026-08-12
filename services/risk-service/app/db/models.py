"""Risk service database models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin, utc_now

from app.db.base import Base


class RiskEvaluation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Evaluation record of order/consumer risk scoring."""

    __tablename__ = "risk_evaluations"

    evaluation_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # ORDER | CONSUMER | RETAILER
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    risk_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 (LOW) to 1.0 (CRITICAL)
    decision: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # PASS | REVIEW | REJECT
    reason_codes_json: Mapped[str] = mapped_column(Text, nullable=False)


class FraudPatternRule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Configurable risk and fraud detection rule."""

    __tablename__ = "fraud_pattern_rules"

    rule_name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    risk_score_impact: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
