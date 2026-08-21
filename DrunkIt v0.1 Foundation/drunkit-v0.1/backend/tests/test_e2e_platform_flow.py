"""Comprehensive End-to-End Multi-Actor Platform Lifecycle Integration Test.

Executes complete consumer discovery -> taste radar matching -> localized stock lookup ->
deterministic compliance check -> idempotent cart checkout -> retailer fulfillment lifecycle ->
brand house intelligence & audit trail verification.
"""

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.seed import seed_master_catalog
from app.models.audit import AuditLog, OutboxEvent
from app.models.catalog import Brand, Product
from app.models.retailer import Retailer, RetailerLocation

STANDARD_CHECKOUT_TIME = datetime(2026, 6, 15, 14, 0, 0, tzinfo=timezone.utc).isoformat()


@pytest.fixture(autouse=True)
def populate_seed_data(db_session: Session) -> None:
    """Populate master seed data and pilot store network before running tests."""
    seed_master_catalog(db_session)


def test_full_platform_end_to_end_lifecycle(client: TestClient, db_session: Session) -> None:
    """Execute complete 6-phase multi-actor integration journey across DrunkIt v0.1."""

    # ──────────────────────────────────────────────────────────────────────────
    # Phase 1: Identity & Multi-Role Authentication
    # ──────────────────────────────────────────────────────────────────────────
    # 1.1 Register Consumer
    client.post(
        "/api/v1/auth/register",
        json={"email": "e2e.shopper@drunkit.in", "password": "ShopperPassword123!", "role": "CONSUMER"},
    )
    consumer_token = client.post(
        "/api/v1/auth/login",
        json={"email": "e2e.shopper@drunkit.in", "password": "ShopperPassword123!"},
    ).json()["access_token"]
    consumer_headers = {"Authorization": f"Bearer {consumer_token}"}

    # 1.2 Register Store Manager (Retailer)
    client.post(
        "/api/v1/auth/register",
        json={"email": "e2e.storekeeper@drunkit.in", "password": "RetailerPassword123!", "role": "RETAILER"},
    )
    retailer_token = client.post(
        "/api/v1/auth/login",
        json={"email": "e2e.storekeeper@drunkit.in", "password": "RetailerPassword123!"},
    ).json()["access_token"]
    retailer_headers = {"Authorization": f"Bearer {retailer_token}"}

    # 1.3 Register Brand Manager
    client.post(
        "/api/v1/auth/register",
        json={"email": "e2e.brandrep@piccadily.in", "password": "BrandPassword123!", "role": "BRAND_MANAGER"},
    )
    brand_token = client.post(
        "/api/v1/auth/login",
        json={"email": "e2e.brandrep@piccadily.in", "password": "BrandPassword123!"},
    ).json()["access_token"]
    brand_headers = {"Authorization": f"Bearer {brand_token}"}

    # ──────────────────────────────────────────────────────────────────────────
    # Phase 2: Consumer Discovery & Semantic Taste Matching
    # ──────────────────────────────────────────────────────────────────────────
    # 2.1 Taste Vector Matcher
    taste_query = {
        "body": 0.85,
        "smokiness": 0.80,
        "sweetness": 0.65,
        "fruitiness": 0.75,
        "preferred_types": ["WHISKY"],
        "limit": 3,
    }
    taste_res = client.post("/api/v1/discovery/taste-match", json=taste_query)
    assert taste_res.status_code == 200
    matched_spirits = taste_res.json()
    assert len(matched_spirits) >= 1
    assert matched_spirits[0]["similarity_score"] > 0.85

    # 2.2 Curated Occasion Collections
    occ_res = client.get("/api/v1/discovery/occasions/peat-and-smoke")
    assert occ_res.status_code == 200
    assert occ_res.json()["hero_tag"] == "BOLD"

    # ──────────────────────────────────────────────────────────────────────────
    # Phase 3: Real-Time Localized Availability & Geospatial Proximity
    # ──────────────────────────────────────────────────────────────────────────
    avail_res = client.get(
        "/api/v1/products/indri-trini-three-wood/availability",
        params={"latitude": 22.5516, "longitude": 88.3524},
    )
    assert avail_res.status_code == 200
    avail_data = avail_res.json()
    assert avail_data["stores_count"] >= 2

    # Pick 750ml SKU at Park Street store (< 1 km)
    target_store = next(
        s for s in avail_data["stores"] if s["volume_ml"] == 750 and "Park Street" in s["location_name"]
    )
    assert target_store["availability_status"] == "IN_STOCK"
    sku_id = target_store["sku_id"]
    location_id = target_store["location_id"]
    expected_price = target_store["price_formatted"]

    # ──────────────────────────────────────────────────────────────────────────
    # Phase 4: Shopping Cart & Compliance-Gated Checkout
    # ──────────────────────────────────────────────────────────────────────────
    # 4.1 Add to Cart
    add_cart_res = client.post(
        "/api/v1/cart/items",
        json={"sku_id": sku_id, "retailer_location_id": location_id, "quantity": 1},
        headers=consumer_headers,
    )
    assert add_cart_res.status_code == 200
    cart_data = add_cart_res.json()
    assert cart_data["item_count"] == 1
    assert cart_data["total_volume_ml"] == 750

    # 4.2 Execute Compliance-Gated Checkout
    idempotency_key = f"e2e-order-key-{uuid.uuid4()}"
    checkout_res = client.post(
        "/api/v1/cart/checkout",
        json={
            "idempotency_key": idempotency_key,
            "channel": "ONLINE_ORDER",
            "consumer_age": 25,
            "is_age_verified": True,
            "current_time": STANDARD_CHECKOUT_TIME,
        },
        headers=consumer_headers,
    )
    assert checkout_res.status_code == 201
    order_data = checkout_res.json()
    order_id = order_data["id"]
    assert order_data["status"] == "CONFIRMED"
    assert order_data["compliance_decision_id"] is not None
    assert order_data["total_formatted"] == expected_price

    # ──────────────────────────────────────────────────────────────────────────
    # Phase 5: Retailer Store Fulfillment Lifecycle
    # ──────────────────────────────────────────────────────────────────────────
    # 5.1 Store Queue Listing
    queue_res = client.get(
        f"/api/v1/retailer/locations/{location_id}/orders",
        headers=retailer_headers,
    )
    assert queue_res.status_code == 200
    queue_data = queue_res.json()
    assert queue_data["pending_fulfillment_count"] >= 1

    # 5.2 Transition: CONFIRMED -> PREPARING
    step1 = client.patch(
        f"/api/v1/retailer/locations/{location_id}/orders/{order_id}/status",
        json={"status": "PREPARING"},
        headers=retailer_headers,
    )
    assert step1.status_code == 200
    assert step1.json()["status"] == "PREPARING"

    # 5.3 Transition: PREPARING -> READY_FOR_PICKUP
    step2 = client.patch(
        f"/api/v1/retailer/locations/{location_id}/orders/{order_id}/status",
        json={"status": "READY_FOR_PICKUP"},
        headers=retailer_headers,
    )
    assert step2.status_code == 200
    assert step2.json()["status"] == "READY_FOR_PICKUP"

    # 5.4 Transition: READY_FOR_PICKUP -> FULFILLED
    step3 = client.patch(
        f"/api/v1/retailer/locations/{location_id}/orders/{order_id}/status",
        json={"status": "FULFILLED"},
        headers=retailer_headers,
    )
    assert step3.status_code == 200
    assert step3.json()["status"] == "FULFILLED"

    # 5.5 Check Store Dashboard GMV
    dash_res = client.get(
        f"/api/v1/retailer/locations/{location_id}/dashboard",
        headers=retailer_headers,
    )
    assert dash_res.status_code == 200
    assert dash_res.json()["total_gmv_minor"] >= 420000

    # ──────────────────────────────────────────────────────────────────────────
    # Phase 6: Brand House Intelligence & Audit Verification
    # ──────────────────────────────────────────────────────────────────────────
    # 6.1 Brand Dashboard
    brand = db_session.query(Brand).filter(Brand.slug == "indri-single-malt").first()
    assert brand is not None

    brand_dash_res = client.get(
        f"/api/v1/brand-portal/brands/{brand.id}/dashboard",
        headers=brand_headers,
    )
    assert brand_dash_res.status_code == 200
    b_dash = brand_dash_res.json()
    assert b_dash["total_orders"] >= 1
    assert b_dash["total_gross_revenue_minor"] >= 420000

    # 6.2 Brand Taste Radar Visualizer
    radar_res = client.get(f"/api/v1/brand-portal/brands/{brand.id}/taste-radar")
    assert radar_res.status_code == 200
    assert len(radar_res.json()) >= 2

    # 6.3 Audit & Outbox Trail Verification
    audit_count = db_session.query(AuditLog).count()
    assert audit_count >= 1

    outbox_events = list(db_session.scalars(select(OutboxEvent)).all())
    event_types = [e.event_type for e in outbox_events]
    assert "ORDER_CREATED" in event_types
    assert "ORDER_STATUS_CHANGED" in event_types
