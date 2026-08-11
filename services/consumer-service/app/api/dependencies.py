from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from faccp_common.database import get_db
from app.services.consumer_service import ConsumerService


def get_consumer_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ConsumerService:
    return ConsumerService(db=db)
