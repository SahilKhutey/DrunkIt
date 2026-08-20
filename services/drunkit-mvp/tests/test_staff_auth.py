"""
Tests for staff (admin/retailer) authentication and authorization.

Covers the gap flagged after production hardening: /v1/admin/* used
to trust any caller. This proves it no longer does, and that a
RETAILER_STAFF account is actually confined to its own retailer's
resources rather than the whole catalog.
"""
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import models
from app.db.session import Base, get_db

ADMIN_EMAIL = "admin@test.local"
ADMIN_PWD = "test-admin-password-123"


@pytest.fixture()
def client(tmp_path, monkeypatch):
    import app.domain.eligibility.policy_store as policy_store
    from app.domain.eligibility.policy_store import clear_cache
    from app.domain.staff_auth.service import create_staff_user
    from app.db import models as db_models
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

    bootstrap_db = TestingSessionLocal()
    create_staff_user(
        bootstrap_db, email=ADMIN_EMAIL, password=ADMIN_PWD, role=db_models.StaffRole.PLATFORM_ADMIN
    )
    bootstrap_db.close()

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


def _admin_headers(client) -> dict:
    resp = client.post("/v1/admin/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PWD})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _create_retailer_with_staff(client, admin_headers, name: str, staff_email: str, staff_password: str):
    r = client.post("/v1/admin/retailers", json={"name": name}, headers=admin_headers).json()
    client.post(f"/v1/admin/retailers/{r['retailer_id']}/verify", headers=admin_headers)
    client.post(
        f"/v1/admin/retailers/{r['retailer_id']}/staff",
        json={"email": staff_email, "password": staff_password},
        headers=admin_headers,
    )
    return r["retailer_id"]


def _retailer_headers(client, email: str, password: str) -> dict:
    resp = client.post("/v1/admin/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


# ---- Unauthenticated access ----

def test_admin_endpoints_reject_unauthenticated_requests(client):
    resp = client.post("/v1/admin/retailers", json={"name": "Sneaky Retailer"})
    assert resp.status_code == 401

    resp = client.post(
        "/v1/admin/stores",
        json={"retailer_id": "x", "name": "x", "state": "X", "city": "x", "latitude": 0, "longitude": 0},
    )
    assert resp.status_code == 401


def test_wrong_staff_password_rejected(client):
    resp = client.post("/v1/admin/auth/login", json={"email": ADMIN_EMAIL, "password": "wrong-password"})
    assert resp.status_code == 401
    assert resp.json()["detail"]["code"] == "INVALID_CREDENTIALS"


def test_consumer_session_cannot_access_admin_endpoints(client):
    """A consumer's bearer token must never satisfy a staff dependency —
    they're issued from entirely separate tables."""
    otp = client.post("/v1/auth/otp/request", json={"phone": "9000000300"}).json()
    verify = client.post("/v1/auth/otp/verify", json={"phone": "9000000300", "code": otp["dev_otp"]})
    consumer_token = verify.json()["access_token"]

    resp = client.post(
        "/v1/admin/retailers",
        json={"name": "Should not work"},
        headers={"Authorization": f"Bearer {consumer_token}"},
    )
    assert resp.status_code == 401


# ---- Role / retailer scoping ----

def test_platform_admin_only_actions_reject_retailer_staff(client):
    admin = _admin_headers(client)
    retailer_id = _create_retailer_with_staff(client, admin, "Retailer A", "staffA@test.local", "password-a-123")
    staff_a = _retailer_headers(client, "staffA@test.local", "password-a-123")

    # Retailer creation is platform-admin-only.
    resp = client.post("/v1/admin/retailers", json={"name": "Should be blocked"}, headers=staff_a)
    assert resp.status_code == 403

    # Product catalog changes are platform-admin-only.
    resp = client.post(
        "/v1/admin/products",
        json={"name": "x", "brand": "x", "category": "beer", "pack_size": "1L"},
        headers=staff_a,
    )
    assert resp.status_code == 403


def test_retailer_staff_cannot_touch_another_retailers_store(client):
    """
    The core regression test for retailer scoping: staff for Retailer
    A must not be able to create or modify a store under Retailer B,
    even though both are valid, authenticated staff accounts.
    """
    admin = _admin_headers(client)
    retailer_a = _create_retailer_with_staff(client, admin, "Retailer A", "staffA2@test.local", "password-a2-123")
    retailer_b = _create_retailer_with_staff(client, admin, "Retailer B", "staffB2@test.local", "password-b2-123")
    staff_a = _retailer_headers(client, "staffA2@test.local", "password-a2-123")

    # Staff A can create a store under their OWN retailer.
    resp = client.post(
        "/v1/admin/stores",
        json={
            "retailer_id": retailer_a, "name": "A's Store", "state": "TESTLAND",
            "city": "Test City", "latitude": 19.0, "longitude": 72.0,
        },
        headers=staff_a,
    )
    assert resp.status_code == 200

    # Staff A must NOT be able to create a store under Retailer B.
    resp = client.post(
        "/v1/admin/stores",
        json={
            "retailer_id": retailer_b, "name": "Intruding Store", "state": "TESTLAND",
            "city": "Test City", "latitude": 19.0, "longitude": 72.0,
        },
        headers=staff_a,
    )
    assert resp.status_code == 403


def test_platform_admin_can_manage_any_retailer(client):
    admin = _admin_headers(client)
    retailer_id = _create_retailer_with_staff(client, admin, "Retailer C", "staffC@test.local", "password-c-123")

    resp = client.post(
        "/v1/admin/stores",
        json={
            "retailer_id": retailer_id, "name": "Admin-created store", "state": "TESTLAND",
            "city": "Test City", "latitude": 19.0, "longitude": 72.0,
        },
        headers=admin,
    )
    assert resp.status_code == 200


def test_delivery_ops_are_platform_admin_only(client):
    admin = _admin_headers(client)
    retailer_id = _create_retailer_with_staff(client, admin, "Retailer D", "staffD@test.local", "password-d-123")
    staff_d = _retailer_headers(client, "staffD@test.local", "password-d-123")

    resp = client.post(
        "/v1/admin/deliveries/nonexistent-id/transition",
        json={"new_status": "PICKED_UP"},
        headers=staff_d,
    )
    # 403 (role check) must fire before the 404 (not found) would —
    # a retailer should not learn whether a delivery ID exists.
    assert resp.status_code == 403
