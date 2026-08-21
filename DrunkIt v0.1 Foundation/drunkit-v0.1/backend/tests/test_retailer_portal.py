"""Comprehensive test suite for Retailer Portal, Bulk POS Feeds, Store Orders, and Dashboard Analytics."""

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.seed import seed_master_catalog
from app.models.catalog import Product
from app.models.commerce import Order
from app.models.inventory import RetailerSKU
from app.models.retailer import Retailer, RetailerLocation

STANDARD_CHECKOUT_TIME = datetime(2026, 6, 15, 14, 0, 0, tzinfo=timezone.utc).isoformat()


@pytest.fixture(autouse=True)
def populate_seed_data(db_session: Session) -> None:
    """Populate master seed data and pilot store network before running tests."""
    seed_master_catalog(db_session)


def _get_retailer_token(client: TestClient, email: str = "store.manager@drunkit.in") -> tuple[str, dict[str, str]]:
    """Helper to register and login a Retailer user returning token and authorization header."""
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "ManagerPassword123!", "role": "RETAILER"},
    )
    token = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "ManagerPassword123!"},
    ).json()["access_token"]
    return token, {"Authorization": f"Bearer {token}"}


def _get_consumer_token(client: TestClient, email: str = "shopper@drunkit.in") -> tuple[str, dict[str, str]]:
    """Helper to register and login a consumer returning token and authorization header."""
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "ShopperPassword123!", "role": "CONSUMER"},
    )
    token = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "ShopperPassword123!"},
    ).json()["access_token"]
    return token, {"Authorization": f"Bearer {token}"}


def test_bulk_inventory_feed_ingestion(client: TestClient, db_session: Session) -> None:
    """Verify bulk POS sync updates inventory snapshots, calculates availability status, and updates prices."""
    token, headers = _get_retailer_token(client, "pos.manager@drunkit.in")

    location = db_session.query(RetailerLocation).filter(RetailerLocation.state_code == "WB").first()
    assert location is not None

    # Retrieve mapped external SKUs for this store
    mapped_skus = list(
        db_session.scalars(
            select(RetailerSKU).where(RetailerSKU.retailer_location_id == location.id)
        ).all()
    )
    assert len(mapped_skus) >= 3

    sku1_ext = mapped_skus[0].external_sku
    sku2_ext = mapped_skus[1].external_sku
    sku3_ext = mapped_skus[2].external_sku

    # Feed payload with mapped POS SKUs and 1 unmapped item
    feed_payload = {
        "source": "POS_CSV_SYNC",
        "items": [
            {"external_sku": sku1_ext, "quantity": 36, "price_minor": 420000},
            {"external_sku": sku2_ext, "quantity": 3, "price_minor": 510000},  # Low stock
            {"external_sku": sku3_ext, "quantity": 0, "price_minor": 270000},   # Out of stock
            {"external_sku": "POS-UNKNOWN-BARCODE-999", "quantity": 10, "price_minor": 100000},  # Unmapped
        ],
    }

    response = client.post(
        f"/api/v1/retailer/locations/{location.id}/inventory/bulk",
        json=feed_payload,
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 4
    assert data["mapped_count"] == 3
    assert data["unmapped_count"] == 1
    assert "POS-UNKNOWN-BARCODE-999" in data["unmapped_skus"]
    assert data["snapshots_created"] == 3
    assert data["prices_updated"] == 3


def test_store_orders_queue_listing(client: TestClient, db_session: Session) -> None:
    """Verify store order queue returns placed orders for the location."""
    # 1. Consumer places order
    c_token, c_headers = _get_consumer_token(client, "buyer.queue@drunkit.in")
    product = db_session.query(Product).filter(Product.slug == "indri-trini-three-wood").first()
    assert product is not None
    sku = product.variants[0].skus[0]
    location = db_session.query(RetailerLocation).filter(RetailerLocation.state_code == "WB").first()
    assert location is not None

    client.post(
        "/api/v1/cart/items",
        json={"sku_id": str(sku.id), "retailer_location_id": str(location.id), "quantity": 1},
        headers=c_headers,
    )
    checkout_res = client.post(
        "/api/v1/cart/checkout",
        json={
            "idempotency_key": f"queue-order-key-{uuid.uuid4()}",
            "consumer_age": 26,
            "is_age_verified": True,
            "current_time": STANDARD_CHECKOUT_TIME,
        },
        headers=c_headers,
    )
    assert checkout_res.status_code == 201

    # 2. Retailer checks order queue
    r_token, r_headers = _get_retailer_token(client, "queue.manager@drunkit.in")
    queue_res = client.get(
        f"/api/v1/retailer/locations/{location.id}/orders",
        headers=r_headers,
    )
    assert queue_res.status_code == 200
    queue_data = queue_res.json()
    assert queue_data["location_id"] == str(location.id)
    assert queue_data["total_orders"] >= 1
    assert queue_data["pending_fulfillment_count"] >= 1


def test_store_order_fulfillment_state_machine(client: TestClient, db_session: Session) -> None:
    """Verify transitioning an order through CONFIRMED -> PREPARING -> READY_FOR_PICKUP -> FULFILLED."""
    # 1. Place order
    c_token, c_headers = _get_consumer_token(client, "buyer.fulfill@drunkit.in")
    product = db_session.query(Product).filter(Product.slug == "indri-trini-three-wood").first()
    sku = product.variants[0].skus[0]
    location = db_session.query(RetailerLocation).filter(RetailerLocation.state_code == "WB").first()

    client.post(
        "/api/v1/cart/items",
        json={"sku_id": str(sku.id), "retailer_location_id": str(location.id), "quantity": 1},
        headers=c_headers,
    )
    order_id = client.post(
        "/api/v1/cart/checkout",
        json={
            "idempotency_key": f"fulfill-order-key-{uuid.uuid4()}",
            "consumer_age": 26,
            "is_age_verified": True,
            "current_time": STANDARD_CHECKOUT_TIME,
        },
        headers=c_headers,
    ).json()["id"]

    r_token, r_headers = _get_retailer_token(client, "fulfill.manager@drunkit.in")

    # Step 1: Transition to PREPARING
    step1 = client.patch(
        f"/api/v1/retailer/locations/{location.id}/orders/{order_id}/status",
        json={"status": "PREPARING"},
        headers=r_headers,
    )
    assert step1.status_code == 200
    assert step1.json()["status"] == "PREPARING"

    # Step 2: Transition to READY_FOR_PICKUP
    step2 = client.patch(
        f"/api/v1/retailer/locations/{location.id}/orders/{order_id}/status",
        json={"status": "READY_FOR_PICKUP"},
        headers=r_headers,
    )
    assert step2.status_code == 200
    assert step2.json()["status"] == "READY_FOR_PICKUP"

    # Step 3: Transition to FULFILLED
    step3 = client.patch(
        f"/api/v1/retailer/locations/{location.id}/orders/{order_id}/status",
        json={"status": "FULFILLED"},
        headers=r_headers,
    )
    assert step3.status_code == 200
    assert step3.json()["status"] == "FULFILLED"


def test_store_order_invalid_state_transition_fails(client: TestClient, db_session: Session) -> None:
    """Verify invalid state transitions (e.g. CONFIRMED -> FULFILLED directly) fail with 422 VALIDATION_FAILED."""
    c_token, c_headers = _get_consumer_token(client, "buyer.invalid@drunkit.in")
    product = db_session.query(Product).first()
    sku = product.variants[0].skus[0]
    location = db_session.query(RetailerLocation).first()

    client.post(
        "/api/v1/cart/items",
        json={"sku_id": str(sku.id), "retailer_location_id": str(location.id), "quantity": 1},
        headers=c_headers,
    )
    order_id = client.post(
        "/api/v1/cart/checkout",
        json={
            "idempotency_key": f"invalid-trans-key-{uuid.uuid4()}",
            "consumer_age": 26,
            "is_age_verified": True,
            "current_time": STANDARD_CHECKOUT_TIME,
        },
        headers=c_headers,
    ).json()["id"]

    r_token, r_headers = _get_retailer_token(client, "invalid.manager@drunkit.in")

    # Attempt illegal jump: CONFIRMED -> FULFILLED
    invalid_res = client.patch(
        f"/api/v1/retailer/locations/{location.id}/orders/{order_id}/status",
        json={"status": "FULFILLED"},
        headers=r_headers,
    )
    assert invalid_res.status_code == 422
    assert invalid_res.json()["error"]["code"] == "VALIDATION_FAILED"


def test_store_dashboard_metrics(client: TestClient, db_session: Session) -> None:
    """Verify GET /api/v1/retailer/locations/{id}/dashboard returns active SKU counts and GMV."""
    r_token, r_headers = _get_retailer_token(client, "dash.manager@drunkit.in")
    location = db_session.query(RetailerLocation).first()
    assert location is not None

    res = client.get(
        f"/api/v1/retailer/locations/{location.id}/dashboard",
        headers=r_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["location_id"] == str(location.id)
    assert data["active_skus_count"] >= 1
    assert "₹" in data["total_gmv_formatted"]


def test_retailer_portal_rbac_protection(client: TestClient, db_session: Session) -> None:
    """Verify consumers are denied (403 Forbidden) from accessing retailer portal endpoints."""
    c_token, c_headers = _get_consumer_token(client, "hacker.consumer@drunkit.in")
    location = db_session.query(RetailerLocation).first()
    assert location is not None

    # Consumer attempts to view store orders
    res = client.get(
        f"/api/v1/retailer/locations/{location.id}/orders",
        headers=c_headers,
    )
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"
