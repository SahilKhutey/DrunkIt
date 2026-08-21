"""Comprehensive test suite for Master Catalog, Brands, Categories, and Products."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.seed import seed_master_catalog
from app.models.catalog import Brand, Category, Product


@pytest.fixture(autouse=True)
def populate_seed_data(db_session: Session) -> None:
    """Populate database with master seed catalog before running catalog tests."""
    seed_master_catalog(db_session)


def test_seed_catalog_integrity(db_session: Session) -> None:
    """Verify seed script populates categories, brands, products, variants, and taste profiles."""
    brands = db_session.query(Brand).all()
    assert len(brands) >= 6

    products = db_session.query(Product).all()
    assert len(products) >= 8

    # Verify Indri Trini has variants, attributes, and taste profile
    indri = db_session.query(Product).filter(Product.slug == "indri-trini-three-wood").first()
    assert indri is not None
    assert indri.brand.name == "Indri Single Malt"
    assert len(indri.variants) == 2  # 750ml and 375ml
    assert indri.taste_profile is not None
    assert indri.taste_profile.spiciness == Decimal("0.7000")
    assert len(indri.attributes) >= 3


def test_list_products_api(client: TestClient) -> None:
    """Verify GET /api/v1/products returns paginated product summaries."""
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 8
    assert len(data["items"]) > 0

    first_item = data["items"][0]
    assert "name" in first_item
    assert "slug" in first_item
    assert "brand_name" in first_item


def test_get_product_detail_api(client: TestClient) -> None:
    """Verify GET /api/v1/products/{id_or_slug} returns full product specification."""
    response = client.get("/api/v1/products/indri-trini-three-wood")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Indri Trini - Three Wood"
    assert data["brand"]["name"] == "Indri Single Malt"
    assert len(data["variants"]) == 2
    assert float(data["taste_profile"]["body"]) == 0.85
    assert len(data["attributes"]) >= 3


def test_get_non_existent_product_returns_404(client: TestClient) -> None:
    """Verify GET /api/v1/products/{id} for non-existent product returns 404."""
    response = client.get("/api/v1/products/non-existent-whisky-slug")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"


def test_product_search_by_query_keyword(client: TestClient) -> None:
    """Verify search filter q matches product name, description, or region."""
    # 1. Search by name keyword
    res_indri = client.get("/api/v1/products", params={"q": "Indri"})
    assert res_indri.status_code == 200
    data_indri = res_indri.json()
    assert data_indri["total"] >= 2
    assert all("Indri" in item["name"] for item in data_indri["items"])

    # 2. Search by region keyword (Goa)
    res_goa = client.get("/api/v1/products", params={"q": "Goa"})
    assert res_goa.status_code == 200
    data_goa = res_goa.json()
    assert any("Stranger & Sons" in item["name"] for item in data_goa["items"])


def test_product_filtering_by_product_type_and_abv(client: TestClient) -> None:
    """Verify multi-faceted filtering by spirit type and ABV range."""
    # Filter for Tequila
    res_tequila = client.get("/api/v1/products", params={"product_type": "TEQUILA"})
    assert res_tequila.status_code == 200
    data_tequila = res_tequila.json()
    assert data_tequila["total"] >= 1
    assert data_tequila["items"][0]["slug"] == "loca-loka-blanco"

    # Filter for High ABV (>= 50%)
    res_high_abv = client.get("/api/v1/products", params={"min_abv": 50.0})
    assert res_high_abv.status_code == 200
    data_high_abv = res_high_abv.json()
    assert data_high_abv["total"] >= 2
    assert all(float(item["abv"]) >= 50.0 for item in data_high_abv["items"])


def test_brands_endpoints(client: TestClient) -> None:
    """Verify GET /api/v1/brands and GET /api/v1/brands/{id}/products."""
    # 1. List brands
    res_brands = client.get("/api/v1/brands")
    assert res_brands.status_code == 200
    brands = res_brands.json()
    assert len(brands) >= 6

    # 2. Get specific brand profile
    res_brand = client.get("/api/v1/brands/amrut-single-malt")
    assert res_brand.status_code == 200
    brand_data = res_brand.json()
    assert brand_data["name"] == "Amrut Single Malt"

    # 3. Get brand catalog
    res_brand_products = client.get("/api/v1/brands/amrut-single-malt/products")
    assert res_brand_products.status_code == 200
    products = res_brand_products.json()
    assert len(products) >= 1
    assert "Amrut Fusion" in products[0]["name"]


def test_categories_tree_endpoint(client: TestClient) -> None:
    """Verify GET /api/v1/categories returns root categories with nested children."""
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) >= 3

    # Find Spirits root category
    spirits_cat = next((c for c in categories if c["slug"] == "spirits"), None)
    assert spirits_cat is not None
    assert len(spirits_cat["children"]) >= 5


def test_create_product_admin_authorized(client: TestClient, db_session: Session) -> None:
    """Verify admin role can create a new canonical product."""
    # 1. Register and login Admin
    client.post(
        "/api/v1/auth/register",
        json={"email": "catalog.admin@drunkit.in", "password": "AdminPassword123!", "role": "ADMIN"},
    )
    admin_token = client.post(
        "/api/v1/auth/login",
        json={"email": "catalog.admin@drunkit.in", "password": "AdminPassword123!"},
    ).json()["access_token"]

    # 2. Get Brand UUID
    brand = db_session.query(Brand).filter(Brand.slug == "amrut-single-malt").first()
    assert brand is not None

    # 3. Create Product
    product_payload = {
        "brand_id": str(brand.id),
        "name": "Amrut Greedy Angels 12YO",
        "slug": "amrut-greedy-angels-12yo",
        "product_type": "WHISKY",
        "region": "Karnataka",
        "abv": 50.0,
        "description": "Ultra rare 12-year-old Indian single malt whisky.",
        "variants": [
            {
                "volume_ml": 750,
                "packaging_type": "CRYSTAL_DECANTER",
                "sku": {"canonical_code": "SKU_AMRUT_GREEDY_ANGELS_750"},
            }
        ],
        "taste_profile": {
            "body": 0.98,
            "sweetness": 0.85,
            "smokiness": 0.50,
            "spiciness": 0.90,
            "fruitiness": 0.85,
        },
    }
    response = client.post(
        "/api/v1/products",
        json=product_payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Amrut Greedy Angels 12YO"
    assert data["variants"][0]["packaging_type"] == "CRYSTAL_DECANTER"


def test_create_product_consumer_forbidden(client: TestClient, db_session: Session) -> None:
    """Verify consumer role is rejected with 403 Forbidden when attempting to create a product."""
    # 1. Register and login Consumer
    client.post(
        "/api/v1/auth/register",
        json={"email": "catalog.consumer@drunkit.in", "password": "Password123!", "role": "CONSUMER"},
    )
    consumer_token = client.post(
        "/api/v1/auth/login",
        json={"email": "catalog.consumer@drunkit.in", "password": "Password123!"},
    ).json()["access_token"]

    brand = db_session.query(Brand).first()
    assert brand is not None

    product_payload = {
        "brand_id": str(brand.id),
        "name": "Unauthorized Whisky",
        "slug": "unauthorized-whisky",
        "product_type": "WHISKY",
    }
    response = client.post(
        "/api/v1/products",
        json=product_payload,
        headers={"Authorization": f"Bearer {consumer_token}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "INSUFFICIENT_PERMISSIONS"
