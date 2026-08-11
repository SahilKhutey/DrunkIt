from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.domain.marketplace import (
    APIKeyIssuer,
    MarketplaceCatalog,
    PlanLimit,
    Subscription,
    UsageEvent,
    UsageMeter,
)
from app.main import create_app


def test_marketplace_catalog_exposes_public_products_and_scopes():
    catalog = MarketplaceCatalog()
    products = catalog.list_public()

    assert [product["code"] for product in products] == [
        "catalog",
        "compliance",
        "orders",
        "verification",
    ]
    assert catalog.scopes_for_products(["catalog", "orders"]) == {
        "catalog:read",
        "orders:read",
        "orders:write",
    }


def test_api_key_issuer_hashes_and_verifies_without_storing_plaintext():
    issuer = APIKeyIssuer(secret="dev-secret")
    material = issuer.issue(app_id="app_123", environment="sandbox")

    assert material.plaintext_key.startswith("faccp_sandbox_")
    assert material.prefix in material.plaintext_key
    assert material.key_hash != material.plaintext_key
    assert issuer.verify(material.plaintext_key, material.key_hash)
    assert not issuer.verify(material.plaintext_key + "x", material.key_hash)


def test_usage_meter_blocks_subscription_after_plan_limit():
    now = datetime.now(timezone.utc)
    subscription = Subscription(
        developer_id="dev_1",
        app_id="app_1",
        product_code="orders",
        plan_code="starter",
        status="active",
        limits=PlanLimit(requests_per_minute=2, requests_per_day=100, requests_per_month=1000),
        monthly_price=Decimal("999"),
    )
    meter = UsageMeter()
    meter.record(UsageEvent("app_1", "orders", "/api/v1/orders", 200, 80, now))
    meter.record(UsageEvent("app_1", "orders", "/api/v1/orders", 201, 120, now))

    decision = meter.allowed(
        subscription,
        window="minute",
        window_start=now - timedelta(minutes=1),
        now=now + timedelta(seconds=1),
    )

    assert decision["allowed"] is False
    assert decision["used"] == 2
    assert decision["remaining"] == 0


def test_usage_summary_tracks_latency_and_errors_per_product():
    meter = UsageMeter()
    meter.record(UsageEvent("app_1", "catalog", "/api/v1/catalog", 200, 50))
    meter.record(UsageEvent("app_1", "catalog", "/api/v1/catalog", 500, 150))
    meter.record(UsageEvent("app_1", "orders", "/api/v1/orders", 201, 90))
    meter.record(UsageEvent("other_app", "catalog", "/api/v1/catalog", 200, 5))

    summary = meter.summarize_by_product("app_1")

    assert summary["catalog"]["requests"] == 2
    assert summary["catalog"]["avg_latency_ms"] == 100
    assert summary["catalog"]["error_rate"] == 0.5
    assert summary["orders"]["requests"] == 1


def test_developer_portal_app_exposes_marketplace_routes():
    app = create_app()
    paths = {route.path for route in app.routes}

    assert "/api/v1/marketplace/products" in paths
    assert "/api/v1/developer-apps/keys" in paths
    assert "/api/v1/subscriptions" in paths
    assert "/api/v1/usage/decisions" in paths
