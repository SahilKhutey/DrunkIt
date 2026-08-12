"""FastAPI dependencies for risk service."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.database import get_db

from app.services.risk_service import RiskService


async def get_event_producer(request: Request):
    producer = getattr(request.app.state, "event_producer", None)
    return producer


def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    return get_db()


def get_risk_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    producer = Depends(get_event_producer),
) -> RiskService:
    return RiskService(db=db, producer=producer)
