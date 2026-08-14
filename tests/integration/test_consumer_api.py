"""Integration tests for Consumer API routes and authorization boundaries."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

root_dir = Path(__file__).resolve().parents[2]
consumer_dir = root_dir / "services" / "consumer"
if str(consumer_dir) not in sys.path:
    sys.path.insert(0, str(consumer_dir))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from faccp_platform.database.base import Base
from faccp_platform.database.session import get_db_session
from faccp_platform.security.tokens import TokenService
from services.consumer.app.main import create_app

app = create_app()
client = TestClient(app)


@pytest.mark.asyncio
async def test_consumer_api_lifecycle():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db_session():
        async with sessionmaker() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    identity_id = uuid.uuid4()
    token_service = TokenService()
    valid_token = token_service.create_access_token(user_id=identity_id)
    headers = {"Authorization": f"Bearer {valid_token}"}

    # 1. Create Consumer
    res_create = client.post(
        "/consumers",
        json={"identity_id": str(identity_id)},
        headers=headers,
    )
    assert res_create.status_code == 201
    data = res_create.json()
    consumer_id = data["id"]
    assert data["status"] == "pending"

    # 2. Retrieve Consumer (Allowed for owner)
    res_get = client.get(f"/consumers/{consumer_id}", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["id"] == consumer_id

    # 3. Retrieve Consumer (Forbidden for different user without admin permission)
    other_identity_id = uuid.uuid4()
    other_token = token_service.create_access_token(user_id=other_identity_id)
    other_headers = {"Authorization": f"Bearer {other_token}"}
    res_forbidden = client.get(f"/consumers/{consumer_id}", headers=other_headers)
    assert res_forbidden.status_code == 403

    # 4. Profile Update
    res_profile = client.patch(
        f"/consumers/{consumer_id}/profile",
        json={"first_name": "John", "last_name": "Doe", "preferences": {"theme": "dark"}},
        headers=headers,
    )
    assert res_profile.status_code == 200
    profile_data = res_profile.json()
    assert profile_data["first_name"] == "John"
    assert profile_data["preferences"]["theme"] == "dark"

    # 5. Mock Verification
    res_verify = client.post(
        f"/consumers/{consumer_id}/verification/mock?method=manual",
        headers=headers,
    )
    assert res_verify.status_code == 200
    verify_data = res_verify.json()
    assert verify_data["status"] == "verified"
    assert verify_data["provider_reference"] == "mock-provider-ref-001"

    app.dependency_overrides.clear()
    await engine.dispose()
