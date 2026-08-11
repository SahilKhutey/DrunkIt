from typing import Annotated
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from faccp_common.database import get_db
from faccp_common.kafka_client import EventProducer
from app.services.order_service import OrderService


async def get_event_producer(request: Request) -> EventProducer | None:
    return getattr(request.app.state, "event_producer", None)


def get_order_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    producer: Annotated[EventProducer | None, Depends(get_event_producer)] = None,
) -> OrderService:
    return OrderService(db=db, producer=producer)
