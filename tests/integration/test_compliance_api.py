"""Integration test for Compliance Eligibility API evaluation."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

root_dir = Path(__file__).resolve().parents[2]
compliance_dir = root_dir / "services" / "compliance"
if str(compliance_dir) not in sys.path:
    sys.path.insert(0, str(compliance_dir))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from faccp_platform.database.base import Base
from faccp_platform.database.session import get_db_session
from services.compliance.app.main import create_app
from services.compliance.app.repositories.jurisdiction import JurisdictionRepository
from services.compliance.app.seed import seed_demo_policy

app = create_app()
client = TestClient(app)


@pytest.mark.asyncio
async def test_compliance_eligibility_api_flow():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db_session():
        async with sessionmaker() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    # Seed jurisdiction & policy
    async with sessionmaker() as session:
        repo = JurisdictionRepository(session)
        jurisdiction = await repo.create("IN", "CG")
        policy = await seed_demo_policy(session, jurisdiction.id)
        jurisdiction_id = str(jurisdiction.id)

    consumer_id = str(uuid.uuid4())
    product_id = str(uuid.uuid4())

    # 1. Evaluate Allow Payload
    allow_payload = {
        "jurisdiction_id": jurisdiction_id,
        "context": {
            "consumer": {
                "consumer_id": consumer_id,
                "age": 25,
                "verified": True,
                "verification_status": "verified",
            },
            "product": {
                "product_id": product_id,
                "category": "spirits",
                "alcohol_type": "whisky",
                "abv": 40.0,
                "quantity": 1,
            },
            "location": {
                "country": "IN",
                "state": "CG",
                "city": "Bilaspur",
            },
            "order": {
                "total_quantity": 1,
                "total_value": 2500.0,
            },
            "timestamp": "2026-08-14T20:30:00Z",
        },
    }

    res_allow = client.post("/eligibility/evaluate", json=allow_payload)
    assert res_allow.status_code == 200
    data_allow = res_allow.json()
    assert data_allow["status"] == "allow"
    assert len(data_allow["results"]) == 3

    # 2. Evaluate Deny Payload (Underage)
    deny_payload = dict(allow_payload)
    deny_payload["context"] = dict(allow_payload["context"])
    deny_payload["context"]["consumer"] = {
        "consumer_id": consumer_id,
        "age": 19,
        "verified": True,
    }

    res_deny = client.post("/eligibility/evaluate", json=deny_payload)
    assert res_deny.status_code == 200
    data_deny = res_deny.json()
    assert data_deny["status"] == "deny"
    assert "age_requirement_failed" in data_deny["reason_codes"]

    app.dependency_overrides.clear()
    await engine.dispose()
