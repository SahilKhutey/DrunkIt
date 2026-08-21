"""Comprehensive test suite for Brand Portal, Regional Analytics, and Taste Radar Visualizations."""

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.seed import seed_master_catalog
from app.models.catalog import Brand, Product
from app.models.retailer import RetailerLocation

STANDARD_CHECKOUT_TIME = datetime(2026, 6, 15, 14, 0, 0, tzinfo=timezone.utc).isoformat()


@pytest.fixture(autouse=True)
def populate_seed_data(db_session: Session) -> None:
    """Populate master seed data and pilot store network before running tests."""
    seed_master_catalog(db_session)


def _get_brand_manager_token(client: TestClient, email: str = "brand.manager@piccadily.in") -> tuple[str, dict[str, str]]:
    """Helper to register and login a Brand Manager user returning token and authorization header."""
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "BrandPassword123!", "role": "BRAND_MANAGER"},
    )
    token = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "BrandPassword123!"},
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


def test_brand_dashboard_metrics_and_top_skus(client: TestClient, db_session: Session) -> None:
    """Verify brand intelligence dashboard computes products, SKUs, licensed stockists, and revenue."""
    token, headers = _get_brand_manager_token(client, "indri.manager@piccadily.in")

    brand = db_session.query(Brand).filter(Brand.slug == "indri-single-malt").first()
    assert brand is not None

    response = client.get(f"/api/v1/brand-portal/brands/{brand.id}/dashboard", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["brand_slug"] == "indri-single-malt"
    assert data["total_products"] >= 2
    assert data["total_skus"] >= 3
    assert data["total_licensed_stockists"] >= 2
    assert len(data["top_performing_skus"]) >= 3
    assert len(data["regional_distribution"]) >= 1
    assert data["regional_distribution"][0]["state_code"] == "IN-WB"


def test_brand_taste_radar_visualizer_and_benchmarks(client: TestClient, db_session: Session) -> None:
    """Verify 6-axis flavor radar visualizations and category benchmark averages."""
    brand = db_session.query(Brand).filter(Brand.slug == "indri-single-malt").first()
    assert brand is not None

    response = client.get(f"/api/v1/brand-portal/brands/{brand.id}/taste-radar")
    assert response.status_code == 200
    radars = response.json()
    assert len(radars) >= 2

    first_radar = radars[0]
    assert "body" in first_radar["radar_axes"]
    assert "smokiness" in first_radar["radar_axes"]
    assert "category_benchmark" in first_radar
    assert "body" in first_radar["category_benchmark"]
    assert len(first_radar["flavor_tags"]) > 0


def test_brand_portal_rbac_protection(client: TestClient, db_session: Session) -> None:
    """Verify consumers are denied (403 Forbidden) from accessing brand house intelligence dashboards."""
    c_token, c_headers = _get_consumer_token(client, "consumer.intruder@drunkit.in")
    brand = db_session.query(Brand).first()
    assert brand is not None

    res = client.get(f"/api/v1/brand-portal/brands/{brand.id}/dashboard", headers=c_headers)
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"


def test_brand_dashboard_with_real_order_revenue(client: TestClient, db_session: Session) -> None:
    """Verify brand revenue and orders count increment accurately after an order is placed."""
    # 1. Place order for Indri 750ml (₹4,200)
    c_token, c_headers = _get_consumer_token(client, "buyer.brandorder@drunkit.in")
    product = db_session.query(Product).filter(Product.slug == "indri-trini-three-wood").first()
    assert product is not None
    sku = next(v for v in product.variants if v.volume_ml == 750).skus[0]
    location = db_session.query(RetailerLocation).filter(RetailerLocation.state_code == "WB").first()

    client.post(
        "/api/v1/cart/items",
        json={"sku_id": str(sku.id), "retailer_location_id": str(location.id), "quantity": 1},
        headers=c_headers,
    )
    client.post(
        "/api/v1/cart/checkout",
        json={
            "idempotency_key": f"brand-rev-test-{uuid.uuid4()}",
            "consumer_age": 27,
            "is_age_verified": True,
            "current_time": STANDARD_CHECKOUT_TIME,
        },
        headers=c_headers,
    )

    # 2. Check Brand Dashboard
    bm_token, bm_headers = _get_brand_manager_token(client, "brand.boss@piccadily.in")
    brand = product.brand
    res = client.get(f"/api/v1/brand-portal/brands/{brand.id}/dashboard", headers=bm_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_orders"] >= 1
    assert data["total_gross_revenue_minor"] >= 420000
    assert "₹4,200.00" in data["total_gross_revenue_formatted"]

    indri_750_sku = next(s for s in data["top_performing_skus"] if s["sku_code"] == sku.canonical_code)
    assert indri_750_sku["units_sold"] >= 1
    assert indri_750_sku["gross_revenue_minor"] >= 420000
