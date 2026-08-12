"""FastAPI dependencies for analytics service."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.database import get_db

from app.services.analytics_service import AnalyticsService


def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    return get_db()


def get_analytics_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> AnalyticsService:
    return AnalyticsService(db=db)
