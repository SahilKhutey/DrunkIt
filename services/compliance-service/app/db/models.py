"""Compliance service database models."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, String, Text, Time
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin, utc_now

from app.db.base import Base


class Policy(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Regulatory Policy definition governing a jurisdiction."""

    __tablename__ = "policies"

    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    jurisdiction: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    min_purchasing_age: Mapped[int] = mapped_column(Integer, default=21, nullable=False)
    max_volume_per_transaction_ml: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_volume_per_day_ml: Mapped[int | None] = mapped_column(Integer, nullable=True)

    sales_start_time: Mapped[time] = mapped_column(Time, default=time(10, 0), nullable=False)
    sales_end_time: Mapped[time] = mapped_column(Time, default=time(22, 0), nullable=False)

    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    rules: Mapped[list["JurisdictionRule"]] = relationship(
        "JurisdictionRule", back_populates="policy", cascade="all, delete-orphan"
    )


class JurisdictionRule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Specific rule under a Policy."""

    __tablename__ = "jurisdiction_rules"

    policy_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rule_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    rule_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    parameters: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    policy: Mapped["Policy"] = relationship("Policy", back_populates="rules")


class DryDayCalendar(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Calendar of mandatory dry days per jurisdiction."""

    __tablename__ = "dry_day_calendars"

    jurisdiction: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    dry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    occasion: Mapped[str] = mapped_column(String(128), nullable=False)
    is_full_day: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)

    __table_args__ = (
        Index("ix_dry_days_jur_date", "jurisdiction", "dry_date", unique=True),
    )


class LicenseRequirement(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """State-specific store license requirements."""

    __tablename__ = "license_requirements"

    jurisdiction: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    license_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    issuing_authority: Mapped[str] = mapped_column(String(128), nullable=False)
    validity_months: Mapped[int] = mapped_column(Integer, default=12, nullable=False)
    requires_renewal_notice_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)


class ComplianceCheck(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Audit record for every compliance evaluation."""

    __tablename__ = "compliance_checks"

    reference_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    check_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    jurisdiction: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    actor_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    is_compliant: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
    failure_reasons: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
