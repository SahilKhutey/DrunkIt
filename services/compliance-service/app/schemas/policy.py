"""Compliance service API schemas."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

DecisionType = Literal["allow", "deny", "review"]


class JurisdictionCreate(BaseModel):
    code: str = Field(min_length=2, max_length=32)
    name: str = Field(min_length=2, max_length=128)
    level: Literal["country", "state", "district", "city", "zone"]
    country_code: str = Field(default="IN", min_length=2, max_length=2)
    parent_code: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)


class JurisdictionResponse(BaseModel):
    id: str
    code: str
    name: str
    level: str
    country_code: str
    is_active: bool


class PolicyCreate(BaseModel):
    jurisdiction_code: str
    policy_type: Literal["age", "hours", "product", "delivery", "pricing", "sale"]
    version: str = Field(min_length=1, max_length=32)
    name: str
    description: str | None = None
    rules: dict[str, Any]
    effective_from: date
    effective_until: date | None = None
    approved_by: str
    source_document: str | None = None

    @field_validator("version")
    @classmethod
    def version_format(cls, v: str) -> str:
        parts = v.split(".")
        if len(parts) < 2 or not all(p.isdigit() for p in parts):
            raise ValueError("Version must be numeric, e.g. '1.0' or '1.0.0'")
        return v


class PolicyResponse(BaseModel):
    id: str
    jurisdiction_code: str
    policy_type: str
    version: str
    name: str
    description: str | None
    rules: dict[str, Any]
    effective_from: date
    effective_until: date | None
    is_active: bool
    approved_by: str
    approved_at: datetime
    checksum: str


class DryDayCreate(BaseModel):
    jurisdiction_code: str
    date: date
    reason: str
    approved_by: str
    is_recurring: bool = False
    recurring_rule: str | None = None


class DryDayResponse(BaseModel):
    id: str
    jurisdiction_code: str
    date: date
    reason: str
    is_recurring: bool
    approved_by: str


class EvaluateRequest(BaseModel):
    subject_id: str
    jurisdiction_code: str
    requested_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    actor: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(
        ...,
        description="Must include: consumer_age, license, product, quantity, delivery_zone"
    )


class EvaluateResponse(BaseModel):
    decision_id: str
    decision: DecisionType
    confidence: float
    reasons: list[str]
    matched_rules: list[str]
    policy_versions: dict[str, str]
    evaluation_ms: int
    details: dict[str, Any]


class DecisionRecord(BaseModel):
    decision_id: str
    subject_type: str
    subject_id: str
    jurisdiction_code: str
    decision: DecisionType
    confidence: float
    reasons: list[dict[str, Any]]
    matched_rules: list[str]
    policy_versions: dict[str, str]
    evaluation_ms: int
    requester: str | None
    created_at: datetime


class OverrideRequest(BaseModel):
    decision_id: str
    override_reason: str = Field(min_length=10, max_length=2000)
    overridden_by: str
