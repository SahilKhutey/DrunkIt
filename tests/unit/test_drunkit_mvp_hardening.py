"""
Tests for production-hardening behavior integrated into the monorepo:
  - X-Request-ID correlation middleware (echoes / generates IDs)
  - Per-phone OTP cooldown (independent of IP-based rate limiter)

These tests run against the FastAPI app using an isolated in-memory
SQLite database, matching the drunkit-mvp1 harness design.
Rate limiting is disabled globally via conftest.py.
"""
import json
import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
drunkit_mvp_path = os.path.join(root_dir, "services", "drunkit-mvp")


def _setup_mvp_env():
    sys.path = [p for p in sys.path if not ("services" in p and p != drunkit_mvp_path)]
    if drunkit_mvp_path not in sys.path:
        sys.path.insert(0, drunkit_mvp_path)
    for mod_name in list(sys.modules.keys()):
        if mod_name == "app" or mod_name.startswith("app."):
            del sys.modules[mod_name]


_setup_mvp_env()

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture()
def client(tmp_path, monkeypatch):
    _setup_mvp_env()

    import app.domain.eligibility.policy_store as policy_store
    from app.domain.eligibility.policy_store import clear_cache
    from app.main import app
    from app.db.session import Base, get_db

    policy_file = tmp_path / "jurisdictions.json"
    policy_file.write_text(
        json.dumps({"default": {"allow_delivery": False, "minimum_age": None}, "states": {}})
    )
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
