"""
Compliance service models.

Stores: policy versions, jurisdiction rules, dry-day calendars,
product classifications, decisions history, exemption records.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Index, Integer, Numeric,
    String, Text, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin, utc_now
from app.db.base import Base


class Jurisdiction(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A regulatory jurisdiction (state, district, country)."""
    __tablename__ = "jurisdictions"

    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    parent_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("jurisdictions.id"), nullable=True)
    level: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # country|state|district|city
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, default="IN")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    parent: Mapped[Jurisdiction | None] = relationship("Jurisdiction", remote_side="Jurisdiction.id", backref="children")


class Policy(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A versioned policy bundle for a jurisdiction."""
    __tablename__ = "policies"

    jurisdiction_id: Mapped[str] = mapped_column(String(36), ForeignKey("jurisdictions.id"), nullable=False, index=True)
    policy_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # sale|delivery|age|product|hours
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    rules: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    effective_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    approved_by: Mapped[str] = mapped_column(String(64), nullable=False)
    approved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_document: Mapped[str | None] = mapped_column(String(256), nullable=True)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        UniqueConstraint("jurisdiction_id", "policy_type", "version", name="uq_policy_version"),
        Index("ix_policy_lookup", "jurisdiction_id", "policy_type", "is_active", "effective_from"),
    )


class DryDay(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Dates on which alcohol sales are prohibited."""
    __tablename__ = "dry_days"

    jurisdiction_id: Mapped[str] = mapped_column(String(36), ForeignKey("jurisdictions.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    reason: Mapped[str] = mapped_column(String(256), nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recurring_rule: Mapped[str | None] = mapped_column(String(128), nullable=True)  # e.g., "last_sunday_of_month"
    overrides_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_by: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        UniqueConstraint("jurisdiction_id", "date", name="uq_jurisdiction_dry_day"),
    )


class ProductClassification(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """How products are classified for regulatory purposes."""
    __tablename__ = "product_classifications"

    jurisdiction_id: Mapped[str] = mapped_column(String(36), ForeignKey("jurisdictions.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # beer|wine|spirit|rtd
    subcategory: Mapped[str | None] = mapped_column(String(64), nullable=True)
    min_age: Mapped[int] = mapped_column(Integer, nullable=False)
    max_abv: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    min_abv: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    permitted_packaging: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    min_bottle_size_ml: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_bottle_size_ml: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quantity_limit_per_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quantity_limit_per_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quantity_limit_per_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    special_restrictions: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)


class Decision(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Append-only history of every compliance decision."""
    __tablename__ = "decisions"

    decision_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    subject_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # order|retailer|product|consumer
    subject_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    jurisdiction_code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    decision: Mapped[str] = mapped_column(String(16), nullable=False, index=True)  # allow|deny|review
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), default=1.0, nullable=False)
    reasons: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list, nullable=False)
    matched_rules: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    policy_versions: Mapped[dict[str, str]] = mapped_column(JSONB, default=dict, nullable=False)
    evaluation_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    requester: Mapped[str | None] = mapped_column(String(64), nullable=True)
    context: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    is_overridden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    overridden_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    overridden_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    override_reason: Mapped[str | None] = mapped_column(Text, nullable=True)


class Exemption(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Granted exemptions from specific rules (e.g., tourist zones)."""
    __tablename__ = "exemptions"

    holder_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    holder_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    jurisdiction_id: Mapped[str] = mapped_column(String(36), ForeignKey("jurisdictions.id"), nullable=False, index=True)
    rule_type: Mapped[str] = mapped_column(String(64), nullable=False)
    rule_reference: Mapped[str] = mapped_column(String(256), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    issued_by: Mapped[str] = mapped_column(String(64), nullable=False)
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_until: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    document_reference: Mapped[str | None] = mapped_column(String(256), nullable=True)


class PolicyMigration(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "policy_migrations"

    migration_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    jurisdiction_code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    policy_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    from_version: Mapped[str] = mapped_column(String(32), nullable=False)
    to_version: Mapped[str] = mapped_column(String(32), nullable=False)
    rules_diff: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    status: Mapped[str] = mapped_column(String(32), default="DRAFT", nullable=False, index=True)
    tests_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tests_passed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tests_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    prepared_by: Mapped[str] = mapped_column(String(64), nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rolled_back_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rollback_reason: Mapped[str | None] = mapped_column(Text, nullable=True)


class PolicyTestCase(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "policy_test_cases"

    migration_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("policy_migrations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    input_context: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    expected_decision: Mapped[str] = mapped_column(String(16), nullable=False)
    actual_decision: Mapped[str | None] = mapped_column(String(16), nullable=True)
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

