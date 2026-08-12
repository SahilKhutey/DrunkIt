"""Analytics service: Metrics Aggregation & Report Snapshotting."""

from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.logging import get_logger

from app.db.models import MetricAggregate, ReportSnapshot
from app.schemas.analytics import MetricAggregateCreate, SnapshotGenerateRequest

logger = get_logger(__name__)


class AnalyticsService:
    """Analytics aggregator recording sales throughput & regulatory report snapshots."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def record_metric(self, payload: MetricAggregateCreate) -> MetricAggregate:
        metric = MetricAggregate(
            metric_name=payload.metric_name,
            dimension_key=payload.dimension_key,
            dimension_value=payload.dimension_value,
            metric_value=payload.metric_value,
            period_start=payload.period_start,
            period_end=payload.period_end,
        )
        self.db.add(metric)
        await self.db.commit()
        await self.db.refresh(metric)
        return metric

    async def generate_snapshot(self, payload: SnapshotGenerateRequest) -> ReportSnapshot:
        code = f"SNP-{secrets.token_hex(4).upper()}"
        snapshot = ReportSnapshot(
            snapshot_code=code,
            report_type=payload.report_type,
            generated_by=payload.generated_by,
            snapshot_data_json=json.dumps(payload.snapshot_data),
        )
        self.db.add(snapshot)
        await self.db.commit()
        await self.db.refresh(snapshot)
        return snapshot

    async def list_metrics(self, metric_name: str | None = None) -> list[MetricAggregate]:
        stmt = select(MetricAggregate).order_by(MetricAggregate.period_start.desc())
        if metric_name:
            stmt = stmt.where(MetricAggregate.metric_name == metric_name)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_snapshots(self) -> list[ReportSnapshot]:
        result = await self.db.execute(
            select(ReportSnapshot).order_by(ReportSnapshot.created_at.desc())
        )
        return list(result.scalars().all())
