"""Compliance service schemas."""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Any


from pydantic import BaseModel, Field


class PolicyCreate(BaseModel):
    code: str = Field(min_length=3, max_length=64)
    title: str = Field(min_length=3, max_length=255)
    description: str | None = None
    jurisdiction: str = Field(min_length=2, max_length=64)
    category: str = "alcohol"
    effective_from: datetime
    effective_until: datetime | None = None
    min_purchasing_age: int = 21
    max_volume_per_transaction_ml: int | None = 3000
    max_volume_per_day_ml: int | None = 9000
    sales_start_time: time = time(10, 0)
    sales_end_time: time = time(22, 0)
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class PolicyResponse(BaseModel):
    id: str
    code: str
    title: str
    description: str | None
    jurisdiction: str
    category: str
    is_active: bool
    effective_from: datetime
    effective_until: datetime | None
    min_purchasing_age: int
    max_volume_per_transaction_ml: int | None
    max_volume_per_day_ml: int | None
    sales_start_time: time
    sales_end_time: time
    created_at: datetime


class DryDayCreate(BaseModel):
    jurisdiction: str
    dry_date: date
    occasion: str
    is_full_day: bool = True
    start_time: time | None = None
    end_time: time | None = None


class DryDayResponse(BaseModel):
    id: str
    jurisdiction: str
    dry_date: date
    occasion: str
    is_full_day: bool


class ComplianceEvaluationRequest(BaseModel):
    reference_id: str
    jurisdiction: str
    actor_id: str
    consumer_age: int
    total_volume_ml: int
    transaction_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    store_license_status: str = "ACTIVE"
    store_license_expiry: date | None = None



class ComplianceEvaluationResult(BaseModel):
    reference_id: str
    jurisdiction: str
    is_compliant: bool
    failure_reasons: list[str] = Field(default_factory=list)
    evaluated_at: datetime
    details: dict[str, Any] = Field(default_factory=dict)
