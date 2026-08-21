"""Comprehensive test suite for Retailer Network, POS SKU mapping, Inventory, and Live Localized Availability."""

import uuid
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.seed import seed_master_catalog
from app.models.catalog import Product, SKU
from app.models.retailer import Jurisdiction, Retailer


@pytest.fixture(autouse=True)
def populate_seed_data(db_session: Session) -> None:
    """Populate database with master seed catalog and pilot stores before running tests."""
    seed_master_catalog(db_session)


def test_retailer_onboarding_and_licencing(client: TestClient, db_session: Session) -> None:
    """Verify retailer registration, physical location creation, and excise licence verification."""
    # 1. Register Admin
    client.post(
        "/api/v1/auth/register",
        json={"email": "retail.admin@drunkit.in", "password": "AdminPassword123!", "role": "ADMIN"},
    )
    admin_token = client.post(
        "/api/v1/auth/login",
        json={"email": "retail.admin@drunkit.in", "password": "AdminPassword123!"},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Create Retailer
    retailer_res = client.post(
        "/api/v1/retailers",
        json={
            "legal_name": "Bangalore Luxury Cellars Pvt Ltd",
            "display_name": "Bangalore Cellars Indiranagar",
        },
        headers=headers,
    )
    assert retailer_res.status_code == 201
    retailer_id = retailer_res.json()["id"]

    # 3. Add Location
    loc_res = client.post(
        f"/api/v1/retailers/{retailer_id}/locations",
        json={
            "name": "Indiranagar Flagship",
            "address": "100 Feet Road, Indiranagar",
            "city": "Bengaluru",
            "state_code": "KA",
            "postal_code": "560038",
            "latitude": 12.9716,
            "longitude": 77.6412,
        },
        headers=headers,
    )
    assert loc_res.status_code == 201
    assert loc_res.json()["city"] == "Bengaluru"

    # 4. Attach Licence
    ka_jur = db_session.query(Jurisdiction).filter(Jurisdiction.state_code == "KA").first()
    assert ka_jur is not None

    lic_res = client.post(
        f"/api/v1/retailers/{retailer_id}/licences",
        json={
            "jurisdiction_id": str(ka_jur.id),
            "licence_number": "KA-EXC-BLR-2026-4421",
            "licence_type": "OFF_TRADE_RETAIL",
        },
        headers=headers,
    )
    assert lic_res.status_code == 201
    assert lic_res.json()["licence_number"] == "KA-EXC-BLR-2026-4421"


def test_sku_mapping_inventory_and_pricing_pipeline(client: TestClient, db_session: Session) -> None:
    """Verify SKU mapping, inventory snapshot ingestion, and active pricing creation."""
    # 1. Setup Admin Token
    client.post(
        "/api/v1/auth/register",
        json={"email": "inventory.admin@drunkit.in", "password": "AdminPassword123!", "role": "ADMIN"},
    )
    admin_token = client.post(
        "/api/v1/auth/login",
        json={"email": "inventory.admin@drunkit.in", "password": "AdminPassword123!"},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Get existing store and SKU
    retailer = db_session.query(Retailer).filter(Retailer.display_name == "Kolkata Spirits Co.").first()
    assert retailer is not None
    location = retailer.locations[0]
    sku = db_session.query(SKU).first()
    assert sku is not None

    # 3. Map Store POS SKU
    map_res = client.post(
        f"/api/v1/retailers/locations/{location.id}/skus/map",
        json={
            "sku_id": str(sku.id),
            "external_sku": "POS-CUSTOM-BARCODE-9988",
            "external_name": "Custom POS Item Label",
        },
        headers=headers,
    )
    assert map_res.status_code == 201
    ret_sku_id = map_res.json()["id"]

    # 4. Ingest Inventory Snapshot
    snap_res = client.post(
        f"/api/v1/retailers/locations/{location.id}/inventory/snapshot",
        json={
            "retailer_sku_id": ret_sku_id,
            "quantity": 48,
            "availability_status": "IN_STOCK",
            "source": "POS_FEED",
        },
        headers=headers,
    )
    assert snap_res.status_code == 201
    assert snap_res.json()["quantity"] == 48

    # 5. Set Price
    price_res = client.post(
        f"/api/v1/retailers/locations/{location.id}/prices",
        json={
            "retailer_sku_id": ret_sku_id,
            "amount_minor": 450000,  # ₹4500.00
            "currency": "INR",
        },
        headers=headers,
    )
    assert price_res.status_code == 201
    assert price_res.json()["amount_minor"] == 450000


def test_product_live_availability_endpoint(client: TestClient) -> None:
    """Verify GET /api/v1/products/{id}/availability returns real-time localized stock and prices."""
    response = client.get("/api/v1/products/indri-trini-three-wood/availability")
    assert response.status_code == 200
    data = response.json()
    assert data["product_slug"] == "indri-trini-three-wood"
    assert data["stores_count"] >= 2

    first_store = data["stores"][0]
    assert first_store["availability_status"] == "IN_STOCK"
    assert first_store["quantity"] > 0
    assert "₹" in first_store["price_formatted"]
    assert first_store["city"] == "Kolkata"
    assert first_store["state_code"] == "WB"


def test_product_availability_geospatial_proximity_sorting(client: TestClient) -> None:
    """Verify proximity sorting by lat/lon returns closest store first."""
    # Consumer is at Park Street (lat: 22.5516, lon: 88.3524)
    response = client.get(
        "/api/v1/products/indri-trini-three-wood/availability",
        params={"latitude": 22.5516, "longitude": 88.3524},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["stores_count"] >= 2

    # Verify Park Street entries are nearest and Salt Lake entries are further
    park_street_stores = [s for s in data["stores"] if "Park Street" in s["location_name"]]
    salt_lake_stores = [s for s in data["stores"] if "Salt Lake" in s["location_name"]]

    assert len(park_street_stores) >= 1
    assert len(salt_lake_stores) >= 1
    assert park_street_stores[0]["distance_km"] < 1.0
    assert salt_lake_stores[0]["distance_km"] > 5.0

    # Nearest store at index 0 should be Park Street
    assert "Park Street" in data["stores"][0]["location_name"]
    # Furthest store at the end should be Salt Lake
    assert "Salt Lake" in data["stores"][-1]["location_name"]


def test_product_availability_jurisdiction_filtering(client: TestClient) -> None:
    """Verify state_code and city filters on live availability."""
    # 1. Filter by West Bengal (WB)
    res_wb = client.get(
        "/api/v1/products/indri-trini-three-wood/availability",
        params={"state_code": "IN-WB"},
    )
    assert res_wb.status_code == 200
    assert res_wb.json()["stores_count"] >= 2

    # 2. Filter by Maharashtra (MH) -> No stores currently seeded in MH
    res_mh = client.get(
        "/api/v1/products/indri-trini-three-wood/availability",
        params={"state_code": "MH"},
    )
    assert res_mh.status_code == 200
    assert res_mh.json()["stores_count"] == 0


def test_retailer_endpoints_rbac_protection(client: TestClient) -> None:
    """Verify consumers are denied (403 Forbidden) from onboarding retailers or modifying inventory."""
    # Register Consumer
    client.post(
        "/api/v1/auth/register",
        json={"email": "consumer.hacker@example.com", "password": "Password123!", "role": "CONSUMER"},
    )
    consumer_token = client.post(
        "/api/v1/auth/login",
        json={"email": "consumer.hacker@example.com", "password": "Password123!"},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {consumer_token}"}

    # Attempt to onboard retailer
    res = client.post(
        "/api/v1/retailers",
        json={"legal_name": "Fake Retailer", "display_name": "Fake Store"},
        headers=headers,
    )
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"
