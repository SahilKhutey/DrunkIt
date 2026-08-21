"""Comprehensive test suite for Delivery Driver Manifests and Statutory Doorstep Handover."""

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.seed import seed_master_catalog
from app.models.catalog import Product
from app.models.commerce import Order
from app.models.retailer import RetailerLocation

STANDARD_CHECKOUT_TIME = datetime(2026, 6, 15, 14, 0, 0, tzinfo=timezone.utc).isoformat()


@pytest.fixture(autouse=True)
def populate_seed_data(db_session: Session) -> None:
    """Populate master seed data before running tests."""
    seed_master_catalog(db_session)


def _setup_confirmed_order(client: TestClient, db_session: Session) -> tuple[str, str, dict[str, str]]:
    """Helper creating a test order advanced to READY_FOR_PICKUP."""
    # Register consumer & place order
    c_email = f"shopper.delivery.{uuid.uuid4()}@drunkit.in"
    client.post(
        "/api/v1/auth/register",
        json={"email": c_email, "password": "ShopperPassword123!", "role": "CONSUMER"},
    )
    c_token = client.post(
        "/api/v1/auth/login",
        json={"email": c_email, "password": "ShopperPassword123!"},
    ).json()["access_token"]
    c_headers = {"Authorization": f"Bearer {c_token}"}

    product = db_session.query(Product).filter(Product.slug == "indri-trini-three-wood").first()
    sku = next(v for v in product.variants if v.volume_ml == 750).skus[0]
    location = db_session.query(RetailerLocation).filter(RetailerLocation.state_code == "WB").first()

    client.post(
        "/api/v1/cart/items",
        json={"sku_id": str(sku.id), "retailer_location_id": str(location.id), "quantity": 1},
        headers=c_headers,
    )
    order_id = client.post(
        "/api/v1/cart/checkout",
        json={
            "idempotency_key": f"delivery-order-{uuid.uuid4()}",
            "channel": "ONLINE_ORDER",
            "consumer_age": 26,
            "is_age_verified": True,
            "current_time": STANDARD_CHECKOUT_TIME,
        },
        headers=c_headers,
    ).json()["id"]

    # Register retailer & advance order to READY_FOR_PICKUP
    r_email = f"retailer.delivery.{uuid.uuid4()}@drunkit.in"
    client.post(
        "/api/v1/auth/register",
        json={"email": r_email, "password": "RetailerPassword123!", "role": "RETAILER"},
    )
    r_token = client.post(
        "/api/v1/auth/login",
        json={"email": r_email, "password": "RetailerPassword123!"},
    ).json()["access_token"]
    r_headers = {"Authorization": f"Bearer {r_token}"}

    client.patch(
        f"/api/v1/retailer/locations/{location.id}/orders/{order_id}/status",
        json={"status": "PREPARING"},
        headers=r_headers,
    )
    client.patch(
        f"/api/v1/retailer/locations/{location.id}/orders/{order_id}/status",
        json={"status": "READY_FOR_PICKUP"},
        headers=r_headers,
    )

    # Register driver
    d_email = f"driver.{uuid.uuid4()}@drunkit.in"
    client.post(
        "/api/v1/auth/register",
        json={"email": d_email, "password": "DriverPassword123!", "role": "RETAILER"},
    )
    d_token = client.post(
        "/api/v1/auth/login",
        json={"email": d_email, "password": "DriverPassword123!"},
    ).json()["access_token"]
    d_headers = {"Authorization": f"Bearer {d_token}"}

    return order_id, str(location.id), d_headers


def test_delivery_assignments_manifest_listing(client: TestClient, db_session: Session) -> None:
    """Verify delivery assignments endpoint lists orders ready for doorstep dispatch."""
    order_id, location_id, d_headers = _setup_confirmed_order(client, db_session)

    res = client.get("/api/v1/delivery/assignments", headers=d_headers)
    assert res.status_code == 200
    assignments = res.json()
    assert len(assignments) >= 1

    matched = next((a for a in assignments if a["order_id"] == order_id), None)
    assert matched is not None
    assert matched["status"] == "READY_FOR_PICKUP"
    assert len(matched["items_summary"]) >= 1


def test_doorstep_id_verification_and_otp_handover_success(client: TestClient, db_session: Session) -> None:
    """Verify successful statutory ID verification (21+) and OTP completion."""
    order_id, location_id, d_headers = _setup_confirmed_order(client, db_session)

    handover_payload = {
        "otp": "4921",
        "verified_id_type": "AADHAAR",
        "recipient_declared_age": 25,
        "latitude": 22.5516,
        "longitude": 88.3524,
    }

    res = client.post(
        f"/api/v1/delivery/orders/{order_id}/verify-and-complete",
        json=handover_payload,
        headers=d_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "FULFILLED"
    assert "Statutory ID verified" in data["message"]


def test_underage_recipient_rejected_at_doorstep(client: TestClient, db_session: Session) -> None:
    """Verify delivery handover fails when recipient age is below 21."""
    order_id, location_id, d_headers = _setup_confirmed_order(client, db_session)

    underage_payload = {
        "otp": "1234",
        "verified_id_type": "DRIVING_LICENCE",
        "recipient_declared_age": 19,
        "latitude": 22.5516,
        "longitude": 88.3524,
    }

    res = client.post(
        f"/api/v1/delivery/orders/{order_id}/verify-and-complete",
        json=underage_payload,
        headers=d_headers,
    )
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "VALIDATION_FAILED"


def test_statutory_delivery_abort_and_store_return(client: TestClient, db_session: Session) -> None:
    """Verify fail-closed statutory delivery cancellation when ID is invalid or recipient is intoxicated."""
    order_id, location_id, d_headers = _setup_confirmed_order(client, db_session)

    abort_payload = {
        "reason": "CONSUMER_INTOXICATED",
        "notes": "Recipient failed statutory sobriety check at door.",
    }

    res = client.post(
        f"/api/v1/delivery/orders/{order_id}/abort-statutory-return",
        json=abort_payload,
        headers=d_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "CANCELLED"
    assert data["abort_reason"] == "CONSUMER_INTOXICATED"
    assert "returned to licensed store" in data["message"]
