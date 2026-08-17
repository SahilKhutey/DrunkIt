"""
Tests for production-hardening behavior: the per-phone OTP cooldown
(independent of the IP-based rate limiter, which is disabled in tests
— see conftest.py) and the request-ID correlation middleware.
"""
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db


@pytest.fixture()
def client(tmp_path, monkeypatch):
    import app.domain.eligibility.policy_store as policy_store
    from app.domain.eligibility.policy_store import clear_cache
    from app.main import app

    policy_file = tmp_path / "jurisdictions.json"
    policy_file.write_text(json.dumps({"default": {"allow_delivery": False, "minimum_age": None}, "states": {}}))
    monkeypatch.setattr(policy_store, "POLICY_FILE", policy_file)
    clear_cache()

    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    clear_cache()


def test_response_carries_request_id_header(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert "x-request-id" in resp.headers
    assert len(resp.headers["x-request-id"]) > 0


def test_request_id_is_echoed_back_when_supplied(client):
    resp = client.get("/health", headers={"X-Request-ID": "my-custom-trace-id"})
    assert resp.headers["x-request-id"] == "my-custom-trace-id"


def test_otp_cooldown_blocks_rapid_repeat_requests(client):
    phone = "9000000200"
    first = client.post("/v1/auth/otp/request", json={"phone": phone})
    assert first.status_code == 200

    second = client.post("/v1/auth/otp/request", json={"phone": phone})
    assert second.status_code == 429
    assert second.json()["detail"]["code"] == "COOLDOWN_ACTIVE"


def test_otp_cooldown_is_per_phone_not_global(client):
    r1 = client.post("/v1/auth/otp/request", json={"phone": "9000000201"})
    assert r1.status_code == 200
    # A different phone number must not be affected by another
    # number's cooldown.
    r2 = client.post("/v1/auth/otp/request", json={"phone": "9000000202"})
    assert r2.status_code == 200
