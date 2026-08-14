"""Async SQLAlchemy session manager and database engine lifecycle."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from faccp_platform.config.settings import get_settings


class DatabaseSessionManager:
    """Async database session manager for platform services."""

    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None

    def init(self, url: str | None = None) -> None:
        if url is None:
            url = get_settings().database_url
        self._engine = create_async_engine(
            url,
            echo=False,
            future=True,
            pool_size=10,
            max_overflow=20,
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    async def close(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        if self._sessionmaker is None:
            self.init()
        assert self._sessionmaker is not None
        session = self._sessionmaker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


_session_manager: DatabaseSessionManager | None = None


def get_session_manager() -> DatabaseSessionManager:
    global _session_manager
    if _session_manager is None:
        _session_manager = DatabaseSessionManager()
    return _session_manager


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an async database session."""
    manager = get_session_manager()
    async with manager.session() as sess:
        yield sess
