"""Comprehensive test suite for Consumer Discovery, Occasion Collections, and Semantic Taste Matching."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.seed import seed_master_catalog


@pytest.fixture(autouse=True)
def populate_seed_data(db_session: Session) -> None:
    """Populate database with master seed catalog before running discovery tests."""
    seed_master_catalog(db_session)


def test_discovery_feed_endpoint(client: TestClient) -> None:
    """Verify GET /api/v1/discovery/feed returns featured brands, occasions, and spotlight products."""
    response = client.get("/api/v1/discovery/feed")
    assert response.status_code == 200
    data = response.json()
    assert "featured_brands" in data
    assert "occasions" in data
    assert "spotlight_products" in data
    assert len(data["featured_brands"]) >= 5
    assert len(data["occasions"]) >= 4
    assert len(data["spotlight_products"]) >= 1


def test_list_occasions_endpoint(client: TestClient) -> None:
    """Verify GET /api/v1/discovery/occasions returns curated occasion collections."""
    response = client.get("/api/v1/discovery/occasions")
    assert response.status_code == 200
    occasions = response.json()
    assert len(occasions) >= 5

    slugs = [oc["slug"] for oc in occasions]
    assert "peat-and-smoke" in slugs
    assert "craft-indie-explorers" in slugs
    assert "celebration-gift" in slugs
    assert "smooth-and-approachable" in slugs


def test_get_occasion_by_slug_peat_and_smoke(client: TestClient) -> None:
    """Verify GET /api/v1/discovery/occasions/peat-and-smoke returns peated spirits."""
    response = client.get("/api/v1/discovery/occasions/peat-and-smoke")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "peat-and-smoke"
    assert data["hero_tag"] == "BOLD"
    assert data["item_count"] >= 2

    item_names = [i["name"] for i in data["items"]]
    assert any("Amrut Fusion" in name or "Indri Diwali" in name or "INCEPTION" in name for name in item_names)


def test_get_occasion_non_existent_returns_404(client: TestClient) -> None:
    """Verify GET /api/v1/discovery/occasions/{invalid_slug} returns 404."""
    response = client.get("/api/v1/discovery/occasions/non-existent-occasion")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"


def test_taste_match_high_smokiness_whisky(client: TestClient) -> None:
    """Verify POST /api/v1/discovery/taste-match returns peated single malts for smokiness queries."""
    payload = {
        "body": 0.90,
        "smokiness": 0.85,
        "spiciness": 0.80,
        "sweetness": 0.60,
        "bitterness": 0.25,
        "fruitiness": 0.70,
        "preferred_types": ["WHISKY"],
        "limit": 5,
    }
    response = client.post("/api/v1/discovery/taste-match", json=payload)
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 2

    top_match = results[0]
    assert top_match["similarity_score"] > 0.90
    assert len(top_match["match_reasons"]) > 0
    # Top match should be a peated malt
    assert any(sub in top_match["product"]["slug"] for sub in ["indri", "amrut", "dyavol"])


def test_taste_match_fresh_botanicals_gin(client: TestClient) -> None:
    """Verify POST /api/v1/discovery/taste-match matches gin botanicals."""
    payload = {
        "body": 0.75,
        "fruitiness": 0.85,
        "spiciness": 0.80,
        "bitterness": 0.35,
        "smokiness": 0.10,
        "sweetness": 0.40,
        "preferred_types": ["GIN"],
        "limit": 3,
    }
    response = client.post("/api/v1/discovery/taste-match", json=payload)
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1

    top_match = results[0]
    assert top_match["similarity_score"] > 0.90
    assert top_match["product"]["slug"] == "stranger-and-sons-gin"
