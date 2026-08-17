from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

connect_args: dict = {}
engine_kwargs: dict = {"future": True}

if settings.database_url.startswith("sqlite"):
    # Needed for SQLite + FastAPI's threaded dev server.
    connect_args = {"check_same_thread": False}
else:
    # Postgres (or any real server-based DB): pool_pre_ping avoids
    # handing out dead connections after a DB restart or idle
    # connection reaping; sizes are conservative single-instance
    # defaults, tune for real traffic before this matters.
    engine_kwargs.update(
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=1800,
    )

engine = create_engine(settings.database_url, connect_args=connect_args, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
