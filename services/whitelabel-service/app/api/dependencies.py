from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.database import get_db
from faccp_common.kafka_client import EventProducer

from app.services.whitelabel_service import WhiteLabelService


async def get_event_producer(request: Request) -> EventProducer | None:
    return getattr(request.app.state, "event_producer", None)


def get_whitelabel_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    producer: Annotated[EventProducer | None, Depends(get_event_producer)] = None,
) -> WhiteLabelService:
    return WhiteLabelService(db=db, producer=producer)
