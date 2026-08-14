"""Integration test for Payment and Risk end-to-end lifecycle."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path
from unittest.mock import AsyncMock
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

root_dir = Path(__file__).resolve().parents[2]
payment_dir = root_dir / "services" / "payment"
risk_dir = root_dir / "services" / "risk"
for p in [str(payment_dir), str(risk_dir), str(root_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from faccp_platform.database.base import Base
from faccp_platform.database.session import get_db_session
from services.payment.app.main import create_app as create_payment_app
from services.payment.app.services.risk_client import RiskClient
from services.risk.app.main import create_app as create_risk_app

payment_app = create_payment_app()
payment_client = TestClient(payment_app)


@pytest.mark.asyncio
async def test_complete_payment_and_webhook_flow(monkeypatch):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db_session():
        async with sessionmaker() as session:
            yield session

    payment_app.dependency_overrides[get_db_session] = override_get_db_session

    # Mock RiskClient to return ALLOW decision
    mock_risk_eval = AsyncMock(
        return_value={"decision": "allow", "risk_level": "low", "score": 0.0, "reasons": []}
    )
    monkeypatch.setattr(RiskClient, "evaluate", mock_risk_eval)

    order_id = str(uuid.uuid4())
    consumer_id = str(uuid.uuid4())
    idempotency_key = "idemp_pay_key_1234567890_test_01"

    payment_payload = {
        "order_id": order_id,
        "consumer_id": consumer_id,
        "amount": 1200.0,
        "currency": "INR",
        "method": "upi",
        "idempotency_key": idempotency_key,
    }

    # 1. Create Payment
    res_pay = payment_client.post("/payments", json=payment_payload)
    assert res_pay.status_code == 201
    pay_data = res_pay.json()
    payment_id = pay_data["id"]
    assert pay_data["status"] in ["requires_action", "processing"]

    # 2. Webhook Event Processing
    event_id = f"evt_{uuid.uuid4().hex}"
    webhook_payload = {
        "event_id": event_id,
        "event_type": "payment.authorized",
        "payment_id": payment_id,
        "provider_payment_id": pay_data["provider_payment_id"] or "mock_123",
        "status": "authorized",
        "amount": "1200.00",
        "currency": "INR",
    }
    res_wh = payment_client.post("/webhooks/payment", json=webhook_payload)
    assert res_wh.status_code == 200
    assert res_wh.json()["status"] == "success"

    # 3. Duplicate Webhook Event returns duplicate status
    res_wh_dup = payment_client.post("/webhooks/payment", json=webhook_payload)
    assert res_wh_dup.status_code == 200
    assert res_wh_dup.json()["status"] == "duplicate"

    # 4. Capture Payment
    res_cap = payment_client.post(f"/payments/{payment_id}/capture", json={})
    assert res_cap.status_code == 200
    assert res_cap.json()["status"] == "captured"

    payment_app.dependency_overrides.clear()
    await engine.dispose()
