"""Comprehensive test suite verifying DrunkIt v0.1 Foundation Hardening."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ComplianceDeniedError,
    ResourceNotFoundError,
    ValidationError,
)
from app.db.repository import BaseRepository
from app.db.uow import SyncUnitOfWork
from app.models.catalog import (
    Brand,
    Category,
    Product,
    ProductVariant,
    SKU,
    TasteProfile,
)
from app.models.compliance import (
    ComplianceCheck,
    ComplianceDecision,
    ComplianceRule,
    ComplianceRuleSet,
)
from app.models.identity import ConsumerProfile, Role, User
from app.models.inventory import InventorySnapshot, Price, RetailerSKU
from app.models.retailer import (
    Jurisdiction,
    Retailer,
    RetailerLicence,
    RetailerLocation,
)


def test_health_endpoint(client: TestClient) -> None:
    """Verify GET /health returns 200 OK with X-Request-ID header."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "X-Request-ID" in response.headers
    assert "X-Response-Time-MS" in response.headers


def test_ready_endpoint(client: TestClient) -> None:
    """Verify GET /ready probe returns dependency health."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "dependencies" in data


def test_version_endpoint(client: TestClient) -> None:
    """Verify GET /version returns application build metadata."""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "drunkit-api"
    assert data["version"] == "0.1.0"


def test_api_v1_root(client: TestClient) -> None:
    """Verify GET /api/v1 returns descriptor with active surfaces."""
    response = client.get("/api/v1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "DrunkIt API"
    assert "consumer" in data["surfaces"]
    assert "compliance" in data["surfaces"]


def test_request_id_middleware_echo(client: TestClient) -> None:
    """Verify incoming X-Request-ID header is preserved and echoed in responses."""
    custom_id = "test-custom-request-id-12345"
    response = client.get("/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == custom_id


def test_models_identity_and_catalog_persistence(db_session: Session) -> None:
    """Verify identity and master catalog models persist correctly with relational integrity."""
    # 1. Create User and Role
    user = User(
        email="founder@drunkit.in",
        phone="+919876543210",
        password_hash="argon2id_mock_hash",
        status="ACTIVE",
    )
    admin_role = Role(code="ADMIN")
    user.roles.append(admin_role)
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert len(user.roles) == 1
    assert user.roles[0].code == "ADMIN"

    # 2. Create Brand, Category, Product, Variant, and SKU
    brand = Brand(
        name="Indri Single Malt",
        slug="indri-single-malt",
        country_code="IN",
        description="Premium Indian Single Malt from Haryana",
    )
    category = Category(
        name="Single Malt Whisky",
        slug="single-malt-whisky",
    )
    db_session.add_all([brand, category])
    db_session.commit()

    product = Product(
        brand_id=brand.id,
        category_id=category.id,
        name="Indri Trini - Three Wood",
        slug="indri-trini-three-wood",
        product_type="WHISKY",
        region="Haryana",
        country_of_origin="IN",
        abv=Decimal("46.00"),
    )
    db_session.add(product)
    db_session.commit()

    variant = ProductVariant(
        product_id=product.id,
        volume_ml=750,
        packaging_type="BOTTLE",
        package_count=1,
    )
    db_session.add(variant)
    db_session.commit()

    sku = SKU(
        variant_id=variant.id,
        canonical_code="SKU_INDRI_TRINI_750",
        barcode="8901234567890",
    )
    taste = TasteProfile(
        product_id=product.id,
        body=Decimal("0.8500"),
        sweetness=Decimal("0.6000"),
        smokiness=Decimal("0.4000"),
        spiciness=Decimal("0.7500"),
        confidence=Decimal("0.9500"),
    )
    db_session.add_all([sku, taste])
    db_session.commit()

    # Query back via repository
    repo = BaseRepository(Product, db_session)
    fetched_product = repo.get_sync(product.id)
    assert fetched_product is not None
    assert fetched_product.brand.name == "Indri Single Malt"
    assert fetched_product.taste_profile.spiciness == Decimal("0.7500")
    assert len(fetched_product.variants) == 1
    assert fetched_product.variants[0].skus[0].canonical_code == "SKU_INDRI_TRINI_750"


def test_models_retailer_inventory_and_pricing(db_session: Session) -> None:
    """Verify retailer network, inventory snapshots, and temporal price models."""
    retailer = Retailer(
        legal_name="Kolkata Spirits Ltd",
        display_name="Kolkata Premium Off-Shop",
        status="ACTIVE",
        licence_status="VERIFIED",
    )
    db_session.add(retailer)
    db_session.commit()

    jurisdiction = Jurisdiction(
        country_code="IN",
        state_code="WB",
        name="West Bengal",
        timezone="Asia/Kolkata",
    )
    db_session.add(jurisdiction)
    db_session.commit()

    location = RetailerLocation(
        retailer_id=retailer.id,
        name="Park Street Store",
        address="12A Park Street",
        city="Kolkata",
        state_code="WB",
        postal_code="700016",
        country_code="IN",
        latitude=Decimal("22.553200"),
        longitude=Decimal("88.351200"),
    )
    db_session.add(location)
    db_session.commit()

    # Create dummy brand first to establish foreign key
    brand = Brand(name="Glenwalk", slug="glenwalk-blended-scotch")
    db_session.add(brand)
    db_session.commit()

    product = Product(
        brand_id=brand.id,
        name="Glenwalk Blended Scotch",
        slug="glenwalk-blended-scotch",
        product_type="WHISKY",
    )
    db_session.add(product)
    db_session.commit()

    variant = ProductVariant(product_id=product.id, volume_ml=750)
    db_session.add(variant)
    db_session.commit()

    sku = SKU(variant_id=variant.id, canonical_code="SKU_GLENWALK_750")
    db_session.add(sku)
    db_session.commit()

    # Map to RetailerSKU
    ret_sku = RetailerSKU(
        retailer_location_id=location.id,
        sku_id=sku.id,
        external_name="Glenwalk Scotch 750ml",
    )
    db_session.add(ret_sku)
    db_session.commit()

    snapshot = InventorySnapshot(
        retailer_sku_id=ret_sku.id,
        quantity=24,
        availability_status="IN_STOCK",
        source="POS_FEED",
    )
    price = Price(
        retailer_sku_id=ret_sku.id,
        amount_minor=155000,  # ₹1550.00
        currency="INR",
        effective_from=datetime.now(timezone.utc),
    )
    db_session.add_all([snapshot, price])
    db_session.commit()

    assert ret_sku.id is not None
    assert len(ret_sku.snapshots) == 1
    assert ret_sku.snapshots[0].quantity == 24
    assert ret_sku.prices[0].amount_minor == 155000


def test_unit_of_work_and_outbox_dispatch(db_session: Session) -> None:
    """Verify UnitOfWork transaction management, outbox recording, and audit trails."""
    uow = SyncUnitOfWork(db_session)
    correlation_id = uuid.uuid4()

    with uow:
        # Record Audit
        audit = uow.record_audit(
            action="PRODUCT_CREATED",
            entity_type="Product",
            correlation_id=correlation_id,
            metadata={"product_slug": "indri-trini"},
        )
        # Publish Outbox Event
        outbox = uow.publish_outbox(
            event_type="PRODUCT_REGISTERED",
            payload={"sku": "SKU_INDRI_TRINI_750", "price": 4200},
            correlation_id=correlation_id,
        )

    assert audit.id is not None
    assert outbox.id is not None
    assert outbox.event_type == "PRODUCT_REGISTERED"
    assert outbox.published_at is None


def test_error_envelope_formatting(client: TestClient) -> None:
    """Verify global exception handlers format standard error envelope."""
    # Test standard 404 from FastAPI route not found
    response = client.get("/api/v1/non-existent-endpoint")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert "request_id" in data["error"]
