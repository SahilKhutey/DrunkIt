"""Risk Scoring & Fraud Assessment Models."""

from __future__ import annotations

from typing import Any
from sqlalchemy import Float, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin
from app.db.base import Base


class RiskAssessment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "risk_assessments"

    subject_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    subject_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # ORDER|CONSUMER|RETAILER
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False, index=True)  # LOW|MEDIUM|HIGH|CRITICAL
    risk_factors: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    recommendation: Mapped[str] = mapped_column(String(32), nullable=False)  # APPROVE|MANUAL_REVIEW|BLOCK
