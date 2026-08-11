from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from faccp_common.database import get_db
from app.services.delivery_service import DeliveryService


def get_delivery_service(db: Annotated[AsyncSession, Depends(get_db)]) -> DeliveryService:
    return DeliveryService(db=db)
