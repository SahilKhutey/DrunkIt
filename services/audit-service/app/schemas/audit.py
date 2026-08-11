"""Audit service schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

Severity = Literal["info", "warning", "error", "critical"]
Result = Literal["success", "failure", "denied", "review", "pending"]


class AuditEventCreate(BaseModel):
    actor_id: str | None = None
    actor_type: Literal["user", "service", "system", "admin"]
    actor_role: str | None = None
    actor_ip: str | None = None
    actor_user_agent: str | None = None
    session_id: str | None = None
    organization_id: str | None = None
    action: str
    resource_type: str
    resource_id: str | None = None
    event_type: str
    description: str | None = None
    result: Result = "success"
    severity: Severity = "info"
    error_code: str | None = None
    service_name: str
    correlation_id: str | None = None
    causation_id: str | None = None
    policy_version: str | None = None
    jurisdiction_code: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    before_state: dict[str, Any] | None = None
    after_state: dict[str, Any] | None = None
    occurred_at: datetime | None = None
    duration_ms: int | None = None


class AuditEventResponse(BaseModel):
    id: str
    event_id: str
    sequence_number: int
    actor_id: str | None
    actor_type: str
    actor_role: str | None
    actor_ip: str | None
    action: str
    resource_type: str
    resource_id: str | None
    event_type: str
    result: str
    severity: str
    service_name: str
    correlation_id: str | None
    payload: dict[str, Any]
    occurred_at: datetime
    received_at: datetime
    previous_hash: str
    event_hash: str


class AuditSearchRequest(BaseModel):
    actor_id: str | None = None
    action: str | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    service_name: str | None = None
    result: Result | None = None
    from_time: datetime | None = None
    to_time: datetime | None = None
    correlation_id: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=500)


class ChainVerificationResult(BaseModel):
    verified_count: int
    broken_count: int
    is_intact: bool
    broken_events: list[dict[str, Any]]
    from_sequence: int
    to_sequence: int | None
    checked_at: str
