"""Compliance domain decision models."""

from __future__ import annotations

import uuid
from pydantic import BaseModel, Field
from .enums import DecisionReasonCode, DecisionStatus


class RuleResult(BaseModel):
    rule_id: uuid.UUID
    passed: bool
    reason: str
    blocking: bool
    reason_code: DecisionReasonCode | None = None


class EligibilityDecision(BaseModel):
    decision_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    status: DecisionStatus
    policy_id: uuid.UUID | None = None
    jurisdiction_id: uuid.UUID
    results: list[RuleResult] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    reason_codes: list[DecisionReasonCode] = Field(default_factory=list)
    engine_version: str = "0.1.0"
