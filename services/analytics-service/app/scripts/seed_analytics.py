"""Seed sample metric aggregates and report snapshots."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from sqlalchemy import select

from app.config import get_settings
from app.db.base import Base
from app.db.models import MetricAggregate, ReportSnapshot
from faccp_common.database import init_engine, session_scope

SAMPLE_METRICS = [
    {
        "metric_name": "ORDER_VOLUME_1H",
        "dimension_key": "STORE_ID",
        "dimension_value": "STR_KA_BLR_001",
        "metric_value": 42.0,
        "period_start": datetime.now(timezone.utc) - timedelta(hours=1),
        "period_end": datetime.now(timezone.utc),
    }
]


async def seed() -> None:
    settings = get_settings()
    init_engine(settings.database_url)
    async with session_scope() as session:
        for m in SAMPLE_METRICS:
            existing = await session.execute(
                select(MetricAggregate).where(
                    MetricAggregate.metric_name == m["metric_name"],
                    MetricAggregate.dimension_value == m["dimension_value"],
                )
            )
            if existing.scalar_one_or_none() is None:
                metric = MetricAggregate(
                    metric_name=m["metric_name"],
                    dimension_key=m["dimension_key"],
                    dimension_value=m["dimension_value"],
                    metric_value=m["metric_value"],
                    period_start=m["period_start"],
                    period_end=m["period_end"],
                )
                session.add(metric)
                print(f"  Metric seeded: {m['metric_name']} -> {m['metric_value']}")

        snapshot = ReportSnapshot(
            snapshot_code="SNP-SEED-001",
            report_type="COMPLIANCE_SUMMARY",
            generated_by="sys_admin_auditor",
            snapshot_data_json=json.dumps({"total_verified_orders": 142, "total_excise_paid_inr": 48500.0}),
        )
        session.add(snapshot)

    print("\n[OK] Seeded analytics metrics and report snapshots.")


if __name__ == "__main__":
    asyncio.run(seed())
