from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from faccp_common.database import get_db
from app.services.verification_service import VerificationService


def get_verification_service(db: Annotated[AsyncSession, Depends(get_db)]) -> VerificationService:
    return VerificationService(db=db)
