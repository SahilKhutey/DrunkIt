"""Eligibility schemas for requests and responses."""

from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from ..engine.context import EligibilityContext


class EligibilityRequest(BaseModel):
    jurisdiction_id: uuid.UUID
    context: EligibilityContext


class RuleResultResponse(BaseModel):
    rule_id: uuid.UUID
    passed: bool
    reason: str
    blocking: bool
    reason_code: str | None = None


class EligibilityResponse(BaseModel):
    decision_id: uuid.UUID
    status: str
    policy_id: uuid.UUID | None = None
    jurisdiction_id: uuid.UUID
    results: list[RuleResultResponse] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    reason_codes: list[str] = Field(default_factory=list)
    engine_version: str = "0.1.0"
