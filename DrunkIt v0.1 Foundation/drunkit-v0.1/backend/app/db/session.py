"""Database configuration and session management for DrunkIt v0.1."""

from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.settings import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy declarative models."""

    pass


# 1. Normalize Synchronous Database URL
sync_url = settings.database_url
if "+asyncpg" in sync_url:
    sync_url = sync_url.replace("+asyncpg", "+psycopg")
elif sync_url.startswith("postgresql://"):
    sync_url = sync_url.replace("postgresql://", "postgresql+psycopg://", 1)

sync_engine_kwargs: dict[str, Any] = {"pool_pre_ping": True}
if sync_url.startswith("sqlite"):
    sync_engine_kwargs = {
        "connect_args": {"check_same_thread": False},
    }
    if ":memory:" in sync_url:
        sync_engine_kwargs["poolclass"] = StaticPool

sync_engine = create_engine(
    sync_url,
    **sync_engine_kwargs,
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_sync_db() -> Generator[Session, None, None]:
    """Dependency for obtaining a synchronous database session."""
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def sync_session_scope() -> Generator[Session, None, None]:
    """Context manager for synchronous transactional database operations."""
    session = SyncSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# 2. Normalize Asynchronous Database URL
async_url = settings.database_url
if async_url.startswith("postgresql://"):
    async_url = async_url.replace("postgresql://", "postgresql+psycopg://", 1)

async_engine: AsyncEngine | None = None
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None

if not async_url.startswith("sqlite"):
    try:
        async_engine = create_async_engine(
            async_url,
            pool_pre_ping=True,
            echo=False,
        )
        AsyncSessionLocal = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    except Exception:
        pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for obtaining an asynchronous database session."""
    if AsyncSessionLocal is None:
        raise RuntimeError("Async database session factory is not configured.")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def async_session_scope() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for asynchronous transactional database operations."""
    if AsyncSessionLocal is None:
        raise RuntimeError("Async database session factory is not configured.")
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
