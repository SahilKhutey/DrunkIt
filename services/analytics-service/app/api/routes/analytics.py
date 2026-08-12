"""Analytics API routes."""

from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, status

from faccp_common.dto import SuccessResponse

from app.api.dependencies import get_analytics_service
from app.schemas.analytics import (
    MetricAggregateCreate, MetricAggregateResponse, ReportSnapshotResponse,
    SnapshotGenerateRequest,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Metrics Aggregator"])


@router.post("/metrics", response_model=SuccessResponse[MetricAggregateResponse], status_code=201)
async def record_metric(
    payload: MetricAggregateCreate,
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> SuccessResponse[MetricAggregateResponse]:
    metric = await service.record_metric(payload)
    return SuccessResponse(data=MetricAggregateResponse(
        id=metric.id, metric_name=metric.metric_name, dimension_key=metric.dimension_key,
        dimension_value=metric.dimension_value, metric_value=metric.metric_value,
        period_start=metric.period_start, period_end=metric.period_end,
        created_at=metric.created_at,
    ), message="Metric aggregate recorded")


@router.get("/metrics", response_model=SuccessResponse[list[MetricAggregateResponse]])
async def list_metrics(
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
    metric_name: str | None = None,
) -> SuccessResponse[list[MetricAggregateResponse]]:
    items = await service.list_metrics(metric_name=metric_name)
    return SuccessResponse(data=[MetricAggregateResponse(
        id=m.id, metric_name=m.metric_name, dimension_key=m.dimension_key,
        dimension_value=m.dimension_value, metric_value=m.metric_value,
        period_start=m.period_start, period_end=m.period_end, created_at=m.created_at,
    ) for m in items])


@router.post("/snapshots", response_model=SuccessResponse[ReportSnapshotResponse], status_code=201)
async def generate_snapshot(
    payload: SnapshotGenerateRequest,
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> SuccessResponse[ReportSnapshotResponse]:
    snapshot = await service.generate_snapshot(payload)
    return SuccessResponse(data=ReportSnapshotResponse(
        id=snapshot.id, snapshot_code=snapshot.snapshot_code, report_type=snapshot.report_type,
        generated_by=snapshot.generated_by, snapshot_data=json.loads(snapshot.snapshot_data_json),
        created_at=snapshot.created_at,
    ), message="Report snapshot generated")


@router.get("/snapshots", response_model=SuccessResponse[list[ReportSnapshotResponse]])
async def list_snapshots(
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> SuccessResponse[list[ReportSnapshotResponse]]:
    snapshots = await service.list_snapshots()
    return SuccessResponse(data=[ReportSnapshotResponse(
        id=s.id, snapshot_code=s.snapshot_code, report_type=s.report_type,
        generated_by=s.generated_by, snapshot_data=json.loads(s.snapshot_data_json),
        created_at=s.created_at,
    ) for s in snapshots])
