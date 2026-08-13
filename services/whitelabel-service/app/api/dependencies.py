"""FastAPI dependencies for whitelabel service."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.database import get_db

from app.services.whitelabel_service import WhitelabelService


def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    return get_db()


def get_whitelabel_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> WhitelabelService:
    return WhitelabelService(db=db)
