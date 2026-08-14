"""Compliance decision model."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ComplianceDecision(BaseModel):
    """Compliance decision result payload."""

    allowed: bool
    state: str
    reasons: list[str] = Field(default_factory=list)
    policy_version: str
    expires_at: str | None = None
