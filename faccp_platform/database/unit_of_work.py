"""Unit of Work pattern for managing transactional boundaries."""

from __future__ import annotations

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from .session import DatabaseSessionManager, get_session_manager


class SqlAlchemyUnitOfWork:
    """Async Unit of Work managing database transactions."""

    def __init__(self, session_manager: DatabaseSessionManager | None = None) -> None:
        self.session_manager = session_manager or get_session_manager()
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> SqlAlchemyUnitOfWork:
        self._generator = self.session_manager.session()
        self.session = await self._generator.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._generator is not None:
            await self._generator.__aexit__(exc_type, exc_val, exc_tb)
            self.session = None

    async def commit(self) -> None:
        if self.session is not None:
            await self.session.commit()

    async def rollback(self) -> None:
        if self.session is not None:
            await self.session.rollback()
