"""Compliance Rule database model."""

from __future__ import annotations

import json
from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..domain.enums import Operator, RuleType


class ComplianceRule(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Specific evaluation rule associated with a CompliancePolicy."""

    __tablename__ = "compliance_rules"

    policy_id: Mapped[str] = mapped_column(String(36), ForeignKey("compliance_policies.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    rule_type: Mapped[RuleType] = mapped_column(Enum(RuleType, name="compliance_rule_type"), nullable=False)
    operator: Mapped[Operator] = mapped_column(Enum(Operator, name="compliance_operator"), nullable=False)
    field: Mapped[str] = mapped_column(String(255), nullable=False)
    value_json: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    blocking: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    @property
    def value(self) -> dict:
        try:
            return json.loads(self.value_json)
        except Exception:
            return {}

    @value.setter
    def value(self, val: dict) -> None:
        self.value_json = json.dumps(val)
