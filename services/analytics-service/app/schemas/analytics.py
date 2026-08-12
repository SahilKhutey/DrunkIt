"""Analytics service API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class MetricAggregateCreate(BaseModel):
    metric_name: str = Field(min_length=3, max_length=64)
    dimension_key: str
    dimension_value: str
    metric_value: float
    period_start: datetime
    period_end: datetime


class MetricAggregateResponse(BaseModel):
    id: str
    metric_name: str
    dimension_key: str
    dimension_value: str
    metric_value: float
    period_start: datetime
    period_end: datetime
    created_at: datetime


class SnapshotGenerateRequest(BaseModel):
    report_type: str = Field(min_length=3, max_length=64)
    generated_by: str
    snapshot_data: dict


class ReportSnapshotResponse(BaseModel):
    id: str
    snapshot_code: str
    report_type: str
    generated_by: str
    snapshot_data: dict
    created_at: datetime
