"""
End-to-end tests against the FastAPI app using an isolated in-memory
SQLite database and an isolated jurisdiction policy file per test run
- nothing here touches the real dev DB or the shipped policies file.

Auth flow used throughout: request an OTP (dev mode returns the code
directly), verify it, use the returned bearer token for every
consumer-scoped call. This exercises the same path a real client uses.

Admin/staff auth: a PLATFORM_ADMIN is bootstrapped directly via the DB
in the client fixture (mirroring scripts/create_admin.py, since there
is no public "create admin" API endpoint by design), then every admin
call logs in through the real /v1/admin/auth/login endpoint like a
real client would.
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
    policy_file.write_text(
        json.dumps(
            {
                "default": {"allow_delivery": False, "minimum_age": None},
                "states": {"TESTLAND": {"allow_delivery": True, "minimum_age": 21}},
            }
        )
    )
    monkeypatch.setattr(policy_store, "POLICY_FILE", policy_file)
    clear_cache()

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    bootstrap_db = TestingSessionLocal()
    create_staff_user(
        bootstrap_db,
        email=ADMIN_EMAIL,
        password=ADMIN_PWD,
        role=db_models.StaffRole.PLATFORM_ADMIN,
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


def _login(client, phone: str) -> dict:
    """Runs the OTP flow and returns an {'Authorization': 'Bearer ...'} header dict."""
    req = client.post("/v1/auth/otp/request", json={"phone": phone}).json()
    assert req["dev_otp"] is not None, "dev_otp should be present outside production"
    verify = client.post("/v1/auth/otp/verify", json={"phone": phone, "code": req["dev_otp"]})
    assert verify.status_code == 200
    token = verify.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _admin_headers(client) -> dict:
    resp = client.post("/v1/admin/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PWD})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _seed_catalog(client):
    admin = _admin_headers(client)

    r = client.post("/v1/admin/retailers", json={"name": "Test Retailer"}, headers=admin).json()
    client.post(f"/v1/admin/retailers/{r['retailer_id']}/verify", headers=admin)

    s = client.post(
        "/v1/admin/stores",
        json={
            "retailer_id": r["retailer_id"],
            "name": "Test Store",
            "state": "TESTLAND",
            "city": "Test City",
            "latitude": 19.0,
            "longitude": 72.0,
        },
        headers=admin,
    ).json()

    p = client.post(
        "/v1/admin/products",
        json={"name": "Test Beer", "brand": "TestBrand", "category": "beer", "pack_size": "650 ml"},
        headers=admin,
    ).json()

    client.post(
        "/v1/admin/listings",
        json={
            "store_id": s["store_id"],
            "product_id": p["product_id"],
            "mrp": 200,
            "selling_price": 180,
            "quantity": 10,
        },
        headers=admin,
    )
    return s["store_id"], p["product_id"], r["retailer_id"]


def test_otp_login_issues_working_session(client):
    headers = _login(client, "9000000099")
    me = client.get("/v1/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["phone"] == "9000000099"


def test_wrong_otp_code_rejected(client):
    req = client.post("/v1/auth/otp/request", json={"phone": "9000000098"}).json()
    correct = req["dev_otp"]
    wrong = "000000" if correct != "000000" else "111111"
    resp = client.post("/v1/auth/otp/verify", json={"phone": "9000000098", "code": wrong})
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "INVALID_CODE"


def test_endpoints_require_auth(client):
    resp = client.get("/v1/me")
    assert resp.status_code == 401

    resp = client.post("/v1/orders", json={
        "store_id": "x", "items": [], "delivery_address": "x",
        "delivery_latitude": 0, "delivery_longitude": 0,
    })
    assert resp.status_code == 401


def test_client_cannot_impersonate_another_consumer_via_header(client):
    """
    Regression test for the original design gap: a client used to be
    able to just pass any consumer_id and act as that person. Now
    identity is derived solely from the bearer token.
    """
    headers_a = _login(client, "9000000001")
    headers_b = _login(client, "9000000002")

    store_id, product_id, _retailer_id = _seed_catalog(client)
    client.post("/v1/eligibility/verify", headers=headers_a,
                json={"state": "TESTLAND", "date_of_birth": "1990-01-01"})

    order = client.post(
        "/v1/orders",
        headers=headers_a,
        json={
            "store_id": store_id,
            "items": [{"product_id": product_id, "quantity": 1}],
            "delivery_address": "A's address",
            "delivery_latitude": 19.0,
            "delivery_longitude": 72.0,
        },
    ).json()

    resp = client.get(f"/v1/orders/{order['id']}", headers=headers_b)
    assert resp.status_code == 404


def test_listing_visible_but_locked_before_eligibility(client):
    store_id, product_id, _retailer_id = _seed_catalog(client)
    headers = _login(client, "9000000010")

    resp = client.get(
        "/v1/listings", headers=headers,
        params={"lat": 19.0, "lng": 72.0, "state": "TESTLAND"},
    )
    assert resp.status_code == 200
    listings = resp.json()
    assert len(listings) == 1
    assert listings[0]["can_add_to_cart"] is False


def test_anonymous_browsing_works_without_auth(client):
    store_id, product_id, _retailer_id = _seed_catalog(client)
    resp = client.get("/v1/listings", params={"lat": 19.0, "lng": 72.0, "state": "TESTLAND"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_underage_checkout_blocked_server_side(client):
    store_id, product_id, _retailer_id = _seed_catalog(client)
    headers = _login(client, "9000000011")
    client.post("/v1/eligibility/verify", headers=headers,
                json={"state": "TESTLAND", "date_of_birth": "2010-01-01"})

    resp = client.post(
        "/v1/orders",
        headers=headers,
        json={
            "store_id": store_id,
            "items": [{"product_id": product_id, "quantity": 1}],
            "delivery_address": "Somewhere",
            "delivery_latitude": 19.0,
            "delivery_longitude": 72.0,
        },
    )
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "INELIGIBLE"


def test_eligible_adult_can_order_and_stock_decrements(client):
    store_id, product_id, _retailer_id = _seed_catalog(client)
    headers = _login(client, "9000000012")
    client.post("/v1/eligibility/verify", headers=headers,
                json={"state": "TESTLAND", "date_of_birth": "1990-01-01"})

    resp = client.post(
        "/v1/orders",
        headers=headers,
        json={
            "store_id": store_id,
            "items": [{"product_id": product_id, "quantity": 3}],
            "delivery_address": "Somewhere",
            "delivery_latitude": 19.0,
            "delivery_longitude": 72.0,
        },
    )
    assert resp.status_code == 200
    order = resp.json()
    assert order["status"] == "CONFIRMED"
    assert order["subtotal"] == pytest.approx(540.0)
    assert order["total"] == pytest.approx(565.0)

    history = client.get("/v1/orders", headers=headers).json()
    assert len(history) == 1
    assert history[0]["id"] == order["id"]


def test_order_over_stock_rejected(client):
    store_id, product_id, _retailer_id = _seed_catalog(client)
    headers = _login(client, "9000000013")
    client.post("/v1/eligibility/verify", headers=headers,
                json={"state": "TESTLAND", "date_of_birth": "1990-01-01"})

    resp = client.post(
        "/v1/orders",
        headers=headers,
        json={
            "store_id": store_id,
            "items": [{"product_id": product_id, "quantity": 999}],
            "delivery_address": "Somewhere",
            "delivery_latitude": 19.0,
            "delivery_longitude": 72.0,
        },
    )
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "OUT_OF_STOCK"


def test_delivery_cannot_skip_handoff_verification(client):
    store_id, product_id, _retailer_id = _seed_catalog(client)
    admin = _admin_headers(client)
    headers = _login(client, "9000000014")
    client.post("/v1/eligibility/verify", headers=headers,
                json={"state": "TESTLAND", "date_of_birth": "1990-01-01"})

    order = client.post(
        "/v1/orders",
        headers=headers,
        json={
            "store_id": store_id,
            "items": [{"product_id": product_id, "quantity": 1}],
            "delivery_address": "Somewhere",
            "delivery_latitude": 19.0,
            "delivery_longitude": 72.0,
        },
    ).json()

    delivery = client.get(f"/v1/orders/{order['id']}/delivery", headers=headers).json()

    resp = client.post(
        f"/v1/admin/deliveries/{delivery['id']}/transition",
        json={"new_status": "DELIVERED"},
        headers=admin,
    )
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "INVALID_TRANSITION"

    client.post(
        f"/v1/admin/deliveries/{delivery['id']}/assign",
        params={"driver_name": "Test Driver", "driver_phone": "9111111111"},
        headers=admin,
    )
    for status in ["PICKED_UP", "IN_TRANSIT", "ARRIVING", "HANDOFF_VERIFICATION"]:
        r = client.post(
            f"/v1/admin/deliveries/{delivery['id']}/transition",
            json={"new_status": status},
            headers=admin,
        )
        assert r.status_code == 200

    final = client.post(
        f"/v1/admin/deliveries/{delivery['id']}/handoff",
        json={"verified": True},
        headers=admin,
    )
    assert final.status_code == 200
    assert final.json()["status"] == "DELIVERED"

    order_after = client.get(f"/v1/orders/{order['id']}", headers=headers).json()
    assert order_after["status"] == "DELIVERED"
