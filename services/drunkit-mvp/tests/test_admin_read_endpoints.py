"""
Tests for the admin/staff read (list) endpoints — the ones a staff
dashboard depends on. The critical property here is identical to the
write-side tests in test_staff_auth.py: a RETAILER_STAFF caller must
never see another retailer's data, even via a list endpoint where
under-filtering is an easy mistake to make.
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
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _setup_retailer_with_store(client, admin_headers, name, staff_email, staff_password):
    r = client.post("/v1/admin/retailers", json={"name": name}, headers=admin_headers).json()
    client.post(f"/v1/admin/retailers/{r['retailer_id']}/verify", headers=admin_headers)
    client.post(
        f"/v1/admin/retailers/{r['retailer_id']}/staff",
        json={"email": staff_email, "password": staff_password},
        headers=admin_headers,
    )
    store = client.post(
        "/v1/admin/stores",
        json={
            "retailer_id": r["retailer_id"], "name": f"{name} Store", "state": "TESTLAND",
            "city": "Test City", "latitude": 19.0, "longitude": 72.0,
        },
        headers=admin_headers,
    ).json()
    login = client.post("/v1/admin/auth/login", json={"email": staff_email, "password": staff_password})
    staff_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    return r["retailer_id"], store["store_id"], staff_headers


def test_list_retailers_is_platform_admin_only(client):
    admin = _admin_headers(client)
    _setup_retailer_with_store(client, admin, "Retailer X", "x@test.local", "password-x-123")

    resp = client.get("/v1/admin/retailers", headers=admin)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    login = client.post("/v1/admin/auth/login", json={"email": "x@test.local", "password": "password-x-123"})
    staff_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    resp = client.get("/v1/admin/retailers", headers=staff_headers)
    assert resp.status_code == 403


def test_list_stores_scoped_to_own_retailer(client):
    admin = _admin_headers(client)
    _, store_a, staff_a = _setup_retailer_with_store(client, admin, "Retailer A", "a@test.local", "password-a-123")
    _, store_b, staff_b = _setup_retailer_with_store(client, admin, "Retailer B", "b@test.local", "password-b-123")

    resp_a = client.get("/v1/admin/stores", headers=staff_a)
    assert resp_a.status_code == 200
    store_ids_a = {s["id"] for s in resp_a.json()}
    assert store_a in store_ids_a
    assert store_b not in store_ids_a  # the core assertion: B is invisible to A

    resp_admin = client.get("/v1/admin/stores", headers=admin)
    all_ids = {s["id"] for s in resp_admin.json()}
    assert store_a in all_ids and store_b in all_ids


def test_list_stores_ignores_spoofed_retailer_id_query_param(client):
    """
    A RETAILER_STAFF caller passing ?retailer_id=<someone else's> must
    not get that retailer's stores back — the query param narrows an
    already-scoped result set, it never widens it.
    """
    admin = _admin_headers(client)
    retailer_a, store_a, staff_a = _setup_retailer_with_store(client, admin, "Retailer C", "c@test.local", "password-c-123")
    retailer_b, store_b, _ = _setup_retailer_with_store(client, admin, "Retailer D", "d@test.local", "password-d-123")

    resp = client.get("/v1/admin/stores", params={"retailer_id": retailer_b}, headers=staff_a)
    assert resp.status_code == 200
    store_ids = {s["id"] for s in resp.json()}
    assert store_b not in store_ids
    assert all(s["retailer_id"] == retailer_a for s in resp.json())


def test_list_listings_requires_retailer_access(client):
    admin = _admin_headers(client)
    _, store_a, staff_a = _setup_retailer_with_store(client, admin, "Retailer E", "e@test.local", "password-e-123")
    _, store_b, staff_b = _setup_retailer_with_store(client, admin, "Retailer F", "f@test.local", "password-f-123")

    # Staff A must not be able to list Store B's listings.
    resp = client.get("/v1/admin/listings", params={"store_id": store_b}, headers=staff_a)
    assert resp.status_code == 403

    # Staff A CAN list their own store's listings (empty, but authorized).
    resp = client.get("/v1/admin/listings", params={"store_id": store_a}, headers=staff_a)
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_orders_requires_retailer_access(client):
    admin = _admin_headers(client)
    _, store_a, staff_a = _setup_retailer_with_store(client, admin, "Retailer G", "g@test.local", "password-g-123")
    _, store_b, staff_b = _setup_retailer_with_store(client, admin, "Retailer H", "h@test.local", "password-h-123")

    resp = client.get("/v1/admin/orders", params={"store_id": store_b}, headers=staff_a)
    assert resp.status_code == 403


def test_list_deliveries_is_platform_admin_only(client):
    admin = _admin_headers(client)
    _, _, staff_a = _setup_retailer_with_store(client, admin, "Retailer I", "i@test.local", "password-i-123")

    resp = client.get("/v1/admin/deliveries", headers=admin)
    assert resp.status_code == 200

    resp = client.get("/v1/admin/deliveries", headers=staff_a)
    assert resp.status_code == 403


def test_list_products_readable_by_both_roles(client):
    admin = _admin_headers(client)
    _, _, staff_a = _setup_retailer_with_store(client, admin, "Retailer J", "j@test.local", "password-j-123")
    client.post(
        "/v1/admin/products",
        json={"name": "Test Product", "brand": "TestBrand", "category": "beer", "pack_size": "1L"},
        headers=admin,
    )

    resp = client.get("/v1/admin/products", headers=staff_a)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
