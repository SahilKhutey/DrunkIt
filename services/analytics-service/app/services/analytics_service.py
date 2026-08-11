"""
Analytics service — ingests events, calculates real-time metrics, builds dashboard data.
"""

import uuid
from datetime import datetime, timezone, date
from decimal import Decimal
from typing import Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.logging import get_logger
from app.db.models import DailyPlatformMetric, DailyStoreMetric, EventArchive

logger = get_logger(__name__)


class AnalyticsService:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def ingest_event(self, event_data: dict[str, Any]) -> EventArchive:
        archive = EventArchive(
            id=str(uuid.uuid4()),
            event_id=event_data.get("event_id", str(uuid.uuid4())),
            event_type=event_data.get("event_type", "unknown"),
            producer=event_data.get("producer", "unknown"),
            tenant_id=event_data.get("tenant_id"),
            user_id=event_data.get("user_id"),
            payload=event_data.get("payload", {}),
            occurred_at=datetime.fromisoformat(event_data["timestamp"]) if "timestamp" in event_data else datetime.now(timezone.utc),
            archived_at=datetime.now(timezone.utc),
        )
        self.db.add(archive)
        await self.db.commit()
        return archive

    async def get_dashboard_summary(self) -> dict[str, Any]:
        result = await self.db.execute(select(func.count(EventArchive.id)))
        total_events = result.scalar() or 0
        return {
            "total_events_archived": total_events,
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
