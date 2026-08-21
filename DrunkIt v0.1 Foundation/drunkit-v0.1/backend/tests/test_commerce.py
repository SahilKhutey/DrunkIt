"""Comprehensive test suite for Shopping Cart, Compliance-Gated Checkout, Idempotency, and Order Lifecycle."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.seed import seed_master_catalog
from app.models.catalog import Product, SKU
from app.models.commerce import Order
from app.models.retailer import Retailer, RetailerLocation

# Deterministic standard checkout business hour (2:00 PM on June 15, 2026)
STANDARD_CHECKOUT_TIME = datetime(2026, 6, 15, 14, 0, 0, tzinfo=timezone.utc).isoformat()


@pytest.fixture(autouse=True)
def populate_seed_data(db_session: Session) -> None:
    """Populate master seed data and pilot store network before running tests."""
    seed_master_catalog(db_session)


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


def test_cart_add_item_and_calculate_totals(client: TestClient, db_session: Session) -> None:
    """Verify adding product variant SKUs to active cart computes quantities, volume, and formatted prices."""
    token, headers = _get_consumer_token(client, "cart.user1@drunkit.in")

    # Get Indri 750ml SKU and Park Street Location
    product = db_session.query(Product).filter(Product.slug == "indri-trini-three-wood").first()
    assert product is not None
    variant_750 = next(v for v in product.variants if v.volume_ml == 750)
    sku_750 = variant_750.skus[0]

    retailer = db_session.query(Retailer).filter(Retailer.display_name == "Kolkata Spirits Co.").first()
    assert retailer is not None
    park_street = retailer.locations[0]

    # 1. Add 2 units to cart
    add_payload = {
        "sku_id": str(sku_750.id),
        "retailer_location_id": str(park_street.id),
        "quantity": 2,
    }
    response = client.post("/api/v1/cart/items", json=add_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["item_count"] == 1
    assert data["total_volume_ml"] == 1500  # 2 * 750ml
    assert data["subtotal_minor"] == 840000  # 2 * ₹4,200.00
    assert "₹8,400.00" in data["subtotal_formatted"]

    # 2. View Cart via GET /api/v1/cart
    get_cart_res = client.get("/api/v1/cart", headers=headers)
    assert get_cart_res.status_code == 200
    cart_data = get_cart_res.json()
    assert cart_data["item_count"] == 1
    assert cart_data["items"][0]["quantity"] == 2
    assert cart_data["items"][0]["product_name"] == "Indri Trini - Three Wood"


def test_cart_remove_item(client: TestClient, db_session: Session) -> None:
    """Verify removing a line item updates cart totals."""
    token, headers = _get_consumer_token(client, "cart.user2@drunkit.in")

    product = db_session.query(Product).filter(Product.slug == "glenwalk-blended-scotch").first()
    assert product is not None
    sku = product.variants[0].skus[0]
    location = db_session.query(RetailerLocation).first()
    assert location is not None

    # Add item
    add_res = client.post(
        "/api/v1/cart/items",
        json={"sku_id": str(sku.id), "retailer_location_id": str(location.id), "quantity": 1},
        headers=headers,
    )
    assert add_res.status_code == 200
    item_id = add_res.json()["items"][0]["id"]

    # Remove item
    del_res = client.delete(f"/api/v1/cart/items/{item_id}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["item_count"] == 0
    assert del_res.json()["subtotal_minor"] == 0


def test_compliance_gated_checkout_adult_success(client: TestClient, db_session: Session) -> None:
    """Verify verified adult checkout passes regulatory gates and produces Confirmed Order with compliance ID."""
    token, headers = _get_consumer_token(client, "checkout.adult@drunkit.in")

    # Get Indri 750ml and Park Street Store in Kolkata (West Bengal)
    product = db_session.query(Product).filter(Product.slug == "indri-trini-three-wood").first()
    assert product is not None
    sku = next(v for v in product.variants if v.volume_ml == 750).skus[0]
    location = db_session.query(RetailerLocation).filter(RetailerLocation.state_code == "WB").first()
    assert location is not None

    # Add to cart
    client.post(
        "/api/v1/cart/items",
        json={"sku_id": str(sku.id), "retailer_location_id": str(location.id), "quantity": 1},
        headers=headers,
    )

    # Checkout with Verified Adult (Age 24, West Bengal LDA is 21)
    idempotency_key = f"checkout-test-key-{uuid.uuid4()}"
    checkout_payload = {
        "idempotency_key": idempotency_key,
        "channel": "ONLINE_ORDER",
        "consumer_age": 24,
        "is_age_verified": True,
        "current_time": STANDARD_CHECKOUT_TIME,
    }
    response = client.post("/api/v1/cart/checkout", json=checkout_payload, headers=headers)
    assert response.status_code == 201
    order_data = response.json()
    assert order_data["status"] == "CONFIRMED"
    assert order_data["total_minor"] == 420000
    assert "₹4,200.00" in order_data["total_formatted"]
    assert order_data["compliance_decision_id"] is not None
    assert len(order_data["items"]) == 1
    assert order_data["items"][0]["product_name"] == "Indri Trini - Three Wood"

    # Verify Cart is now cleared
    cart_res = client.get("/api/v1/cart", headers=headers)
    assert cart_res.json()["item_count"] == 0


def test_compliance_gated_checkout_underage_denial(client: TestClient, db_session: Session) -> None:
    """Verify underage checkout is blocked by the compliance engine with 403 COMPLIANCE_DENIED."""
    token, headers = _get_consumer_token(client, "checkout.underage@drunkit.in")

    product = db_session.query(Product).filter(Product.slug == "indri-trini-three-wood").first()
    assert product is not None
    sku = product.variants[0].skus[0]
    location = db_session.query(RetailerLocation).filter(RetailerLocation.state_code == "WB").first()
    assert location is not None

    client.post(
        "/api/v1/cart/items",
        json={"sku_id": str(sku.id), "retailer_location_id": str(location.id), "quantity": 1},
        headers=headers,
    )

    # Attempt Checkout with Underage (Age 19 vs WB LDA 21)
    checkout_payload = {
        "idempotency_key": str(uuid.uuid4()),
        "channel": "ONLINE_ORDER",
        "consumer_age": 19,
        "is_age_verified": True,
        "current_time": STANDARD_CHECKOUT_TIME,
    }
    response = client.post("/api/v1/cart/checkout", json=checkout_payload, headers=headers)
    assert response.status_code == 403
    data = response.json()
    assert data["error"]["code"] == "COMPLIANCE_DENIED"
    assert "UNDERAGE_DENIED" in str(data["error"]["details"])

    # Verify Cart remains intact
    cart_res = client.get("/api/v1/cart", headers=headers)
    assert cart_res.json()["item_count"] == 1


def test_idempotent_checkout_prevents_duplicate_orders(client: TestClient, db_session: Session) -> None:
    """Verify executing checkout twice with identical idempotency key returns the same order without creating duplicates."""
    token, headers = _get_consumer_token(client, "checkout.idempotent@drunkit.in")

    product = db_session.query(Product).filter(Product.slug == "glenwalk-blended-scotch").first()
    assert product is not None
    sku = product.variants[0].skus[0]
    location = db_session.query(RetailerLocation).filter(RetailerLocation.state_code == "WB").first()
    assert location is not None

    client.post(
        "/api/v1/cart/items",
        json={"sku_id": str(sku.id), "retailer_location_id": str(location.id), "quantity": 1},
        headers=headers,
    )

    idempotency_key = "idempotent-order-uuid-unique-12345"
    payload = {
        "idempotency_key": idempotency_key,
        "channel": "ONLINE_ORDER",
        "consumer_age": 28,
        "is_age_verified": True,
        "current_time": STANDARD_CHECKOUT_TIME,
    }

    # First Checkout
    res1 = client.post("/api/v1/cart/checkout", json=payload, headers=headers)
    assert res1.status_code == 201
    order1 = res1.json()

    # Second Checkout with identical idempotency key
    res2 = client.post("/api/v1/cart/checkout", json=payload, headers=headers)
    assert res2.status_code == 201
    order2 = res2.json()

    assert order1["id"] == order2["id"]
    assert order1["total_minor"] == order2["total_minor"]

    # Verify DB contains exactly 1 order
    orders = db_session.scalars(
        select(Order).where(Order.idempotency_key == idempotency_key)
    ).all()
    assert len(orders) == 1


def test_get_order_and_list_orders(client: TestClient, db_session: Session) -> None:
    """Verify GET /api/v1/orders and GET /api/v1/orders/{order_id} endpoints."""
    token, headers = _get_consumer_token(client, "order.viewer@drunkit.in")

    product = db_session.query(Product).first()
    assert product is not None
    sku = product.variants[0].skus[0]
    location = db_session.query(RetailerLocation).first()
    assert location is not None

    # Add item & Checkout
    client.post(
        "/api/v1/cart/items",
        json={"sku_id": str(sku.id), "retailer_location_id": str(location.id), "quantity": 1},
        headers=headers,
    )
    checkout_res = client.post(
        "/api/v1/cart/checkout",
        json={
            "idempotency_key": f"order-view-key-{uuid.uuid4()}",
            "consumer_age": 25,
            "is_age_verified": True,
            "current_time": STANDARD_CHECKOUT_TIME,
        },
        headers=headers,
    )
    order_id = checkout_res.json()["id"]

    # 1. List Orders
    list_res = client.get("/api/v1/orders", headers=headers)
    assert list_res.status_code == 200
    orders_list = list_res.json()
    assert len(orders_list) >= 1
    assert orders_list[0]["id"] == order_id

    # 2. Get Order Detail
    detail_res = client.get(f"/api/v1/orders/{order_id}", headers=headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["id"] == order_id
    assert len(detail_data["items"]) == 1
