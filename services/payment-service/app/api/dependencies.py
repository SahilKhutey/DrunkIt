"""FastAPI dependencies for payment service."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.database import get_db

from app.services.payment_service import PaymentService


async def get_event_producer(request: Request):
    producer = getattr(request.app.state, "event_producer", None)
    return producer


def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    return get_db()


def get_payment_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    producer = Depends(get_event_producer),
) -> PaymentService:
    return PaymentService(db=db, producer=producer)
