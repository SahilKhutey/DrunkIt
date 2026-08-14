"""Integration test for Order API lifecycle and idempotency enforcement."""

from __future__ import annotations

import sys
import uuid
from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

root_dir = Path(__file__).resolve().parents[2]
order_dir = root_dir / "services" / "order"
if str(order_dir) not in sys.path:
    sys.path.insert(0, str(order_dir))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from faccp_platform.database.base import Base
from faccp_platform.database.session import get_db_session
from services.order.app.main import create_app
from services.order.app.services.compliance_client import ComplianceClient

app = create_app()
client = TestClient(app)


@pytest.mark.asyncio
async def test_order_api_lifecycle_and_idempotency(monkeypatch):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db_session():
        async with sessionmaker() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    # Mock ComplianceClient to return ALLOW decision
    mock_evaluate = AsyncMock(
        return_value={"status": "allow", "decision_id": str(uuid.uuid4()), "policy_version": "1.0.0"}
    )
    monkeypatch.setattr(ComplianceClient, "evaluate", mock_evaluate)

    consumer_id = str(uuid.uuid4())
    jurisdiction_id = str(uuid.uuid4())
    idempotency_key = "idemp_key_1234567890_test_api"

    order_payload = {
        "consumer_id": consumer_id,
        "jurisdiction_id": jurisdiction_id,
        "idempotency_key": idempotency_key,
        "items": [
            {
                "product_id": str(uuid.uuid4()),
                "product_name": "Premium Malt Whisky",
                "quantity": 1.0,
                "unit_price": 2500.0,
            }
        ],
        "delivery_fee": 100.0,
    }

    # 1. First request creates order
    res1 = client.post("/orders", json=order_payload)
    assert res1.status_code == 201
    data1 = res1.json()
    order_id = data1["id"]
    assert data1["status"] == "pending_payment"
    assert float(data1["total"]) == 2600.0

    # 2. Idempotent second request returns existing order
    res2 = client.post("/orders", json=order_payload)
    assert res2.status_code == 201
    data2 = res2.json()
    assert data2["id"] == order_id

    # 3. Retrieve order by ID
    res_get = client.get(f"/orders/{order_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == order_id

    app.dependency_overrides.clear()
    await engine.dispose()
