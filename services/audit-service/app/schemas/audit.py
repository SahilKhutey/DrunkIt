"""Audit service API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AuditEntryCreate(BaseModel):
    event_type: str = Field(min_length=3, max_length=128)
    actor_id: str
    actor_role: str
    resource_type: str
    resource_id: str
    payload_json: str


class AuditEntryResponse(BaseModel):
    id: str
    sequence_number: int
    event_id: str
    event_type: str
    actor_id: str
    actor_role: str
    resource_type: str
    resource_id: str
    previous_hash: str
    current_hash: str
    recorded_at: datetime


class ChainVerificationResponse(BaseModel):
    is_valid: bool
    total_entries: int
    corrupted_sequence: int | None = None
    message: str
