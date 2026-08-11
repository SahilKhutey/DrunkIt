from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from faccp_common.database import get_db
from app.services.risk_service import RiskService


def get_risk_service(db: Annotated[AsyncSession, Depends(get_db)]) -> RiskService:
    return RiskService(db=db)
