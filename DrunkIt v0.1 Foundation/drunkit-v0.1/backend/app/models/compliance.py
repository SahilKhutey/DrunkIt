"""Compliance domain models for versioned statutory rulesets, evaluations, and decision trails."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.session import Base

# Use JSONB on PostgreSQL, fall back to JSON on SQLite/other
JsonType = JSONB().with_variant(JSON(), "sqlite")


class ComplianceRuleSet(Base):
    """Versioned regulatory policy ruleset for a specific jurisdiction."""

    __tablename__ = "compliance_rule_sets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    jurisdiction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jurisdictions.id", ondelete="CASCADE"),
        nullable=False,
    )
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE")
    source_reference: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("jurisdiction_id", "version", name="uq_jurisdiction_ruleset_version"),
    )

    # Relationships
    rules: Mapped[list["ComplianceRule"]] = relationship(
        "ComplianceRule",
        back_populates="rule_set",
        cascade="all, delete-orphan",
    )


class ComplianceRule(Base):
    """Discrete statutory rule definition within a ruleset."""

    __tablename__ = "compliance_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    rule_set_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("compliance_rule_sets.id", ondelete="CASCADE"),
        nullable=False,
    )
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    product_class: Mapped[str | None] = mapped_column(String(50), nullable=True)
    licence_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    age_requirement: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ordering_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    delivery_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    payment_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    conditions_json: Mapped[dict[str, Any]] = mapped_column(JsonType, nullable=False, default=dict)
    source_reference: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    rule_set: Mapped["ComplianceRuleSet"] = relationship("ComplianceRuleSet", back_populates="rules")


class ComplianceCheck(Base):
    """Execution context and input parameters of a statutory compliance check."""

    __tablename__ = "compliance_checks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    correlation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    consumer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    jurisdiction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jurisdictions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
    )
    retailer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("retailers.id", ondelete="SET NULL"),
        nullable=True,
    )
    context_json: Mapped[dict[str, Any]] = mapped_column(JsonType, nullable=False, default=dict)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    decision: Mapped["ComplianceDecision | None"] = relationship(
        "ComplianceDecision",
        back_populates="compliance_check",
        uselist=False,
        cascade="all, delete-orphan",
    )


class ComplianceDecision(Base):
    """Immutable record of an evaluated compliance determination."""

    __tablename__ = "compliance_decisions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    compliance_check_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("compliance_checks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    decision: Mapped[str] = mapped_column(String(20), nullable=False)  # ALLOW, DENY, REVIEW
    reason_codes: Mapped[list[Any]] = mapped_column(JsonType, nullable=False, default=list)
    required_checks: Mapped[list[Any]] = mapped_column(JsonType, nullable=False, default=list)
    rule_set_version: Mapped[str] = mapped_column(String(50), nullable=False)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    compliance_check: Mapped["ComplianceCheck"] = relationship(
        "ComplianceCheck",
        back_populates="decision",
    )
