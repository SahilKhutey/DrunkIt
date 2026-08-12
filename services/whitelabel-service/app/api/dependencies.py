from typing import AsyncGenerator
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from faccp_common.database import get_db_session
from app.services.whitelabel_service import WhiteLabelService


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session(request.app.state.db_session_factory):
        yield session


async def get_whitelabel_service(request: Request) -> AsyncGenerator[WhiteLabelService, None]:
    async for session in get_db_session(request.app.state.db_session_factory):
        producer = getattr(request.app.state, "producer", None)
        yield WhiteLabelService(db=session, producer=producer)
