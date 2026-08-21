"""Pytest test configuration and fixtures for DrunkIt v0.1 backend."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - ensure all models are registered
from app.db.session import Base, get_sync_db
from app.main import app as fastapi_app

# In-memory SQLite engine with StaticPool for fast, isolated test runs
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(autouse=True)
def reset_test_database() -> Generator[None, None, None]:
    """Ensure a pristine, isolated database schema for each test execution."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provide a clean, isolated database session for each unit test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with overridden database session dependency."""

    def override_get_sync_db() -> Generator[Session, None, None]:
        yield db_session

    fastapi_app.dependency_overrides[get_sync_db] = override_get_sync_db

    with TestClient(fastapi_app) as test_client:
        yield test_client

    fastapi_app.dependency_overrides.clear()
