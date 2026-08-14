"""Unit tests for faccp_platform Database + Migration Framework."""

from __future__ import annotations

import sys
from pathlib import Path
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from faccp_platform.config.settings import get_settings
from faccp_platform.database.base import Base
from faccp_platform.database.models import UserAccountModel, TenantModel, AuditLogModel, OutboxEventModel
from faccp_platform.database.repository import BaseRepository
from faccp_platform.database.session import DatabaseSessionManager, get_session_manager


def test_database_url_configuration():
    settings = get_settings()
    url = settings.database_url
    assert url.startswith("postgresql+asyncpg://")
    assert "faccp" in url
    assert "5432" in url


def test_platform_metadata_models_registration():
    table_names = set(Base.metadata.tables.keys())
    expected_tables = {
        "faccp_user_accounts",
        "faccp_tenants",
        "faccp_audit_logs",
        "faccp_outbox_events",
    }
    assert expected_tables.issubset(table_names)


@pytest.mark.asyncio
async def test_in_memory_repository_and_session():
    # Use SQLite async for lightweight unit testing of models and repositories
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with sessionmaker() as session:
        repo = BaseRepository(UserAccountModel, session)

        # Create
        user = await repo.create(
            email="test_admin@example.com",
            password_hash="argon2_hashed_secret",
            role="ADMIN",
        )
        assert user.id is not None
        assert user.email == "test_admin@example.com"
        assert user.role == "ADMIN"

        # Read
        fetched = await repo.get_by_id(user.id)
        assert fetched is not None
        assert fetched.email == "test_admin@example.com"

        # List
        all_users = await repo.list_all()
        assert len(all_users) == 1

        # Update
        updated = await repo.update(user, role="SUPER_ADMIN")
        assert updated.role == "SUPER_ADMIN"

        # Delete
        await repo.delete(user)
        deleted = await repo.get_by_id(user.id)
        assert deleted is None

    await engine.dispose()
