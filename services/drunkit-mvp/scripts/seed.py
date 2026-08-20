"""
Seeds a minimal demo dataset so the API is testable end-to-end
immediately after `uvicorn app.main:app` starts.

NOTE: uses "MAHARASHTRA" purely as a placeholder jurisdiction key with
allow_delivery=true injected directly into the policy cache for demo
purposes. Real jurisdiction data belongs in policies/jurisdictions.json
after legal review — see the "_comment" field in that file.

Run with:  python -m scripts.seed
"""
from __future__ import annotations

import json
from pathlib import Path

from app.db.models import (
    InventoryItem,
    Listing,
    ListingStatus,
    PriceRecord,
    Product,
    Retailer,
    RetailerStatus,
    StaffRole,
    Store,
)
from app.db.session import Base, SessionLocal, engine
from app.domain.staff_auth.service import StaffAuthError, create_staff_user

POLICY_FILE = Path(__file__).resolve().parents[1] / "policies" / "jurisdictions.json"

DEMO_ADMIN_EMAIL = "admin@demo.local"
DEMO_ADMIN_PWD = "demo-admin-password-123"
DEMO_RETAILER_STAFF_EMAIL = "retailer@demo.local"
DEMO_RETAILER_STAFF_PWD = "demo-retailer-password-123"


def ensure_demo_jurisdiction() -> None:
    data = json.loads(POLICY_FILE.read_text())
    data["states"]["DEMO_STATE"] = {
        "allow_delivery": True,
        "minimum_age": 21,
        "delivery_mode": "demo_only",
        "legal_basis_ref": "DEMO DATA ONLY — NOT FOR PRODUCTION",
        "notes": "Local seed/demo jurisdiction. Replace before any real launch.",
    }
    POLICY_FILE.write_text(json.dumps(data, indent=2))


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_demo_jurisdiction()

    db = SessionLocal()
    try:
        retailer = Retailer(name="Demo Wine & Spirits", status=RetailerStatus.VERIFIED)
        db.add(retailer)
        db.flush()

        store = Store(
            retailer_id=retailer.id,
            name="Demo Store - Central",
            state="DEMO_STATE",
            city="Demo City",
            latitude=19.0760,
            longitude=72.8777,
        )
        db.add(store)
        db.flush()

        products = [
            Product(name="Kingfisher Premium", brand="Kingfisher", category="beer",
                     pack_size="650 ml", abv_percent=4.8),
            Product(name="Old Monk Rum", brand="Old Monk", category="rum",
                     pack_size="750 ml", abv_percent=42.8),
            Product(name="Sula Cabernet Shiraz", brand="Sula", category="wine",
                     pack_size="750 ml", abv_percent=13.5),
        ]
        db.add_all(products)
        db.flush()

        prices_and_stock = [
            (products[0], 180, 150, 200),
            (products[1], 850, 780, 80),
            (products[2], 950, 890, 40),
        ]
        for product, mrp, sp, qty in prices_and_stock:
            db.add(PriceRecord(store_id=store.id, product_id=product.id,
                                mrp_paise=mrp * 100, selling_price_paise=sp * 100))
            db.add(InventoryItem(store_id=store.id, product_id=product.id, quantity=qty))
            db.add(Listing(store_id=store.id, product_id=product.id, status=ListingStatus.ACTIVE))

        db.commit()

        # Demo staff accounts — dev/test convenience only. Real
        # deployments should use scripts/create_admin.py for the first
        # admin, then have that admin create retailer staff via
        # POST /v1/admin/retailers/{id}/staff, not hardcoded credentials.
        try:
            create_staff_user(
                db, email=DEMO_ADMIN_EMAIL, password=DEMO_ADMIN_PWD, role=StaffRole.PLATFORM_ADMIN
            )
            print(f"Demo platform admin: {DEMO_ADMIN_EMAIL} / {DEMO_ADMIN_PWD}")
        except StaffAuthError:
            print(f"Demo platform admin already exists: {DEMO_ADMIN_EMAIL}")

        try:
            create_staff_user(
                db,
                email=DEMO_RETAILER_STAFF_EMAIL,
                password=DEMO_RETAILER_STAFF_PWD,
                role=StaffRole.RETAILER_STAFF,
                retailer_id=retailer.id,
            )
            print(f"Demo retailer staff: {DEMO_RETAILER_STAFF_EMAIL} / {DEMO_RETAILER_STAFF_PWD}")
        except StaffAuthError:
            print(f"Demo retailer staff already exists: {DEMO_RETAILER_STAFF_EMAIL}")

        print(f"Seeded retailer={retailer.id} store={store.id}")
        print("Try: GET /v1/listings?lat=19.076&lng=72.8777&state=DEMO_STATE")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
