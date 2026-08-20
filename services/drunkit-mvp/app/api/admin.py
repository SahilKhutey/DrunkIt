"""
Admin/ops API.

Every endpoint now requires a valid staff session (see
app/domain/staff_auth and app/api/deps.py). Permission matrix:

  - Retailer creation/verification, product catalog, delivery/driver
    ops -> PLATFORM_ADMIN only. Retailer legitimacy, the shared
    product catalog, and driver dispatch are platform-level decisions
    in this architecture, not something individual retailers control.
  - Store creation, listing/price/inventory management -> PLATFORM_ADMIN
    OR the RETAILER_STAFF user who belongs to that specific retailer
    (checked via check_retailer_access() against the resource's
    retailer_id, never trusted from the request body alone).

Read/list endpoints follow the same matrix: a RETAILER_STAFF caller
never sees another retailer's stores, listings, or orders — scoping is
applied in the query itself, not filtered out after the fact.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import check_retailer_access, get_current_staff, require_platform_admin
from app.db import models
from app.db.session import get_db
from app.domain.delivery.service import DeliveryError, mark_handoff_verified, transition
from app.domain.staff_auth.service import StaffAuthError, create_staff_user
from app.schemas.schemas import (
    AdminDeliveryView,
    AdminListingView,
    AdminOrderItemView,
    AdminOrderView,
    DeliveryTransitionRequest,
    DeliveryView,
    HandoffVerifyRequest,
    ListingCreate,
    ProductCreate,
    ProductView,
    RetailerCreate,
    RetailerStaffCreate,
    RetailerView,
    StaffAccountView,
    StoreCreate,
    StoreView,
)

router = APIRouter(prefix="/v1/admin", tags=["admin"])


# ---- Retailers (platform admin only) ----

@router.post("/retailers", response_model=dict)
def create_retailer(
    payload: RetailerCreate,
    db: Session = Depends(get_db),
    _staff: models.StaffUser = Depends(require_platform_admin),
):
    retailer = models.Retailer(
        name=payload.name,
        license_number=payload.license_number,
        status=models.RetailerStatus.PENDING,
    )
    db.add(retailer)
    db.commit()
    db.refresh(retailer)
    return {"retailer_id": retailer.id, "status": retailer.status.value}


@router.post("/retailers/{retailer_id}/verify", response_model=dict)
def verify_retailer(
    retailer_id: str,
    db: Session = Depends(get_db),
    _staff: models.StaffUser = Depends(require_platform_admin),
):
    """
    Marks a retailer VERIFIED. In production this must be gated on an
    actual license check, not a bare API call — flagged here so it
    isn't mistaken for a real verification workflow.
    """
    retailer = db.query(models.Retailer).filter_by(id=retailer_id).first()
    if retailer is None:
        raise HTTPException(status_code=404, detail="Retailer not found.")
    retailer.status = models.RetailerStatus.VERIFIED
    db.add(retailer)
    db.commit()
    return {"retailer_id": retailer.id, "status": retailer.status.value}


@router.get("/retailers", response_model=list[RetailerView])
def list_retailers(
    db: Session = Depends(get_db),
    _staff: models.StaffUser = Depends(require_platform_admin),
):
    retailers = db.query(models.Retailer).order_by(models.Retailer.created_at.desc()).all()
    return [
        RetailerView(
            id=r.id, name=r.name, license_number=r.license_number,
            status=r.status.value, created_at=r.created_at.isoformat(),
        )
        for r in retailers
    ]


@router.get("/retailers/{retailer_id}/staff", response_model=list[StaffAccountView])
def list_retailer_staff(
    retailer_id: str,
    db: Session = Depends(get_db),
    staff: models.StaffUser = Depends(get_current_staff),
):
    check_retailer_access(staff, retailer_id)
    accounts = db.query(models.StaffUser).filter_by(retailer_id=retailer_id).all()
    return [
        StaffAccountView(
            id=a.id, email=a.email, role=a.role.value, retailer_id=a.retailer_id,
            active=a.active, created_at=a.created_at.isoformat(),
        )
        for a in accounts
    ]


@router.post("/retailers/{retailer_id}/staff", response_model=dict)
def create_retailer_staff(
    retailer_id: str,
    payload: RetailerStaffCreate,
    db: Session = Depends(get_db),
    _staff: models.StaffUser = Depends(require_platform_admin),
):
    """
    Platform admin creates the login for a retailer's own staff — see
    the "no public self-registration" note on RetailerStaffCreate.
    Typically called right after verify_retailer() during onboarding.
    """
    retailer = db.query(models.Retailer).filter_by(id=retailer_id).first()
    if retailer is None:
        raise HTTPException(status_code=404, detail="Retailer not found.")
    try:
        staff = create_staff_user(
            db,
            email=payload.email,
            password=payload.password,
            role=models.StaffRole.RETAILER_STAFF,
            retailer_id=retailer_id,
        )
    except StaffAuthError as e:
        raise HTTPException(status_code=422, detail={"code": e.code, "message": e.message})
    return {"staff_id": staff.id, "email": staff.email, "retailer_id": retailer_id}


# ---- Stores / catalog / listings (admin, or the retailer's own staff) ----

@router.post("/stores", response_model=dict)
def create_store(
    payload: StoreCreate,
    db: Session = Depends(get_db),
    staff: models.StaffUser = Depends(get_current_staff),
):
    check_retailer_access(staff, payload.retailer_id)

    retailer = db.query(models.Retailer).filter_by(id=payload.retailer_id).first()
    if retailer is None:
        raise HTTPException(status_code=404, detail="Retailer not found.")
    store = models.Store(
        retailer_id=retailer.id,
        name=payload.name,
        state=payload.state.strip().upper().replace(" ", "_"),
        city=payload.city,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    db.add(store)
    db.commit()
    db.refresh(store)
    return {"store_id": store.id}


@router.get("/stores", response_model=list[StoreView])
def list_stores(
    retailer_id: str | None = Query(None),
    staff: models.StaffUser = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """
    PLATFORM_ADMIN sees all stores (optionally filtered by
    retailer_id). RETAILER_STAFF is always scoped to their own
    retailer_id regardless of what's passed in the query — a query
    param is never trusted for authorization, only for narrowing an
    already-authorized result set.
    """
    query = db.query(models.Store)
    if staff.role == models.StaffRole.RETAILER_STAFF:
        query = query.filter(models.Store.retailer_id == staff.retailer_id)
    elif retailer_id:
        query = query.filter(models.Store.retailer_id == retailer_id)

    stores = query.all()
    return [
        StoreView(
            id=s.id, retailer_id=s.retailer_id, retailer_name=s.retailer.name,
            name=s.name, state=s.state, city=s.city,
            latitude=s.latitude, longitude=s.longitude,
            is_open=s.is_open, active=s.active,
        )
        for s in stores
    ]


@router.post("/products", response_model=dict)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _staff: models.StaffUser = Depends(require_platform_admin),
):
    # The product catalog is shared/platform-owned (see the original
    # architecture's Product Master vs. Listing separation) — a
    # retailer lists against the existing catalog, they don't add to it.
    product = models.Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return {"product_id": product.id}


@router.get("/products", response_model=list[ProductView])
def list_products(
    _staff: models.StaffUser = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    # Both roles can read the shared catalog — RETAILER_STAFF needs it
    # to pick a product_id when creating a listing, they just can't
    # add to it (see create_product's PLATFORM_ADMIN-only gate above).
    products = db.query(models.Product).filter_by(active=True).all()
    return [
        ProductView(
            id=p.id, name=p.name, brand=p.brand, category=p.category,
            variant=p.variant, pack_size=p.pack_size, active=p.active,
        )
        for p in products
    ]


@router.post("/listings", response_model=dict)
def create_listing(
    payload: ListingCreate,
    db: Session = Depends(get_db),
    staff: models.StaffUser = Depends(get_current_staff),
):
    store = db.query(models.Store).filter_by(id=payload.store_id).first()
    product = db.query(models.Product).filter_by(id=payload.product_id).first()
    if store is None or product is None:
        raise HTTPException(status_code=404, detail="Store or product not found.")

    # The listing's retailer comes from the STORE, not from anything
    # in the request body — payload.store_id already fixes which
    # retailer this belongs to, so that's what gets checked.
    check_retailer_access(staff, store.retailer_id)

    listing = (
        db.query(models.Listing).filter_by(store_id=store.id, product_id=product.id).first()
    )
    if listing is None:
        listing = models.Listing(store_id=store.id, product_id=product.id)
        db.add(listing)
    listing.status = models.ListingStatus.ACTIVE

    price = db.query(models.PriceRecord).filter_by(store_id=store.id, product_id=product.id).first()
    if price is None:
        price = models.PriceRecord(
            store_id=store.id,
            product_id=product.id,
            mrp_paise=int(payload.mrp * 100),
            selling_price_paise=int(payload.selling_price * 100),
        )
    else:
        price.mrp_paise = int(payload.mrp * 100)
        price.selling_price_paise = int(payload.selling_price * 100)
    db.add(price)

    inventory = (
        db.query(models.InventoryItem).filter_by(store_id=store.id, product_id=product.id).first()
    )
    if inventory is None:
        inventory = models.InventoryItem(store_id=store.id, product_id=product.id, quantity=payload.quantity)
    else:
        inventory.quantity = payload.quantity
    db.add(inventory)

    db.commit()
    db.refresh(listing)
    return {"listing_id": listing.id, "status": listing.status.value}


@router.get("/listings", response_model=list[AdminListingView])
def list_listings_for_store(
    store_id: str = Query(...),
    staff: models.StaffUser = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    store = db.query(models.Store).filter_by(id=store_id).first()
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found.")
    check_retailer_access(staff, store.retailer_id)

    listings = db.query(models.Listing).filter_by(store_id=store_id).all()
    views = []
    for listing in listings:
        product = listing.product
        price = db.query(models.PriceRecord).filter_by(store_id=store_id, product_id=product.id).first()
        inventory = db.query(models.InventoryItem).filter_by(store_id=store_id, product_id=product.id).first()
        views.append(
            AdminListingView(
                listing_id=listing.id, store_id=store_id, product_id=product.id,
                product_name=product.name, brand=product.brand, pack_size=product.pack_size,
                status=listing.status.value,
                mrp=price.mrp_paise / 100 if price else None,
                selling_price=price.selling_price_paise / 100 if price else None,
                quantity=inventory.quantity if inventory else None,
            )
        )
    return views


@router.get("/orders", response_model=list[AdminOrderView])
def list_orders_for_store(
    store_id: str = Query(...),
    staff: models.StaffUser = Depends(get_current_staff),
    db: Session = Depends(get_db),
):
    """
    Order fulfillment view for a store — a retailer needs to see
    what's been ordered from them to prep and hand off. Deliberately
    does not expose which consumer placed the order beyond the
    delivery address already required for fulfilment.
    """
    store = db.query(models.Store).filter_by(id=store_id).first()
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found.")
    check_retailer_access(staff, store.retailer_id)

    orders = (
        db.query(models.Order)
        .filter_by(store_id=store_id)
        .order_by(models.Order.created_at.desc())
        .all()
    )
    return [
        AdminOrderView(
            id=o.id, status=o.status.value, total=o.total_paise / 100,
            created_at=o.created_at.isoformat(), delivery_address=o.delivery_address,
            items=[
                AdminOrderItemView(
                    product_name=i.product.name, quantity=i.quantity, unit_price=i.unit_price_paise / 100
                )
                for i in o.items
            ],
        )
        for o in orders
    ]


# ---- Delivery ops (platform admin only — driver dispatch is a platform
# resource, not something individual retailers control in this MVP) ----

@router.get("/deliveries", response_model=list[AdminDeliveryView])
def list_deliveries(
    status: str | None = Query(None, description="Filter by DeliveryStatus, e.g. REQUESTED"),
    _staff: models.StaffUser = Depends(require_platform_admin),
    db: Session = Depends(get_db),
):
    query = db.query(models.Delivery)
    if status:
        try:
            query = query.filter(models.Delivery.status == models.DeliveryStatus(status))
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Unknown delivery status: {status}")

    deliveries = query.order_by(models.Delivery.created_at.desc()).all()
    return [
        AdminDeliveryView(
            id=d.id, order_id=d.order_id, store_id=d.order.store_id, store_name=d.order.store.name,
            status=d.status.value, driver_name=d.driver_name, driver_phone=d.driver_phone,
            eta_min_minutes=d.eta_min_minutes, eta_max_minutes=d.eta_max_minutes,
            created_at=d.created_at.isoformat(),
        )
        for d in deliveries
    ]

@router.post("/deliveries/{delivery_id}/assign", response_model=DeliveryView)
def assign_driver(
    delivery_id: str,
    driver_name: str,
    driver_phone: str,
    db: Session = Depends(get_db),
    _staff: models.StaffUser = Depends(require_platform_admin),
):
    delivery = db.query(models.Delivery).filter_by(id=delivery_id).first()
    if delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found.")
    delivery.driver_name = driver_name
    delivery.driver_phone = driver_phone
    db.add(delivery)
    db.commit()
    try:
        delivery = transition(db, delivery=delivery, new_status=models.DeliveryStatus.ASSIGNED)
    except DeliveryError as e:
        raise HTTPException(status_code=422, detail={"code": e.code, "message": e.message})
    return _delivery_view(delivery)


@router.post("/deliveries/{delivery_id}/transition", response_model=DeliveryView)
def transition_delivery(
    delivery_id: str,
    payload: DeliveryTransitionRequest,
    db: Session = Depends(get_db),
    _staff: models.StaffUser = Depends(require_platform_admin),
):
    delivery = db.query(models.Delivery).filter_by(id=delivery_id).first()
    if delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found.")
    try:
        new_status = models.DeliveryStatus(payload.new_status)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Unknown delivery status: {payload.new_status}")
    try:
        delivery = transition(db, delivery=delivery, new_status=new_status, detail=payload.detail)
    except DeliveryError as e:
        raise HTTPException(status_code=422, detail={"code": e.code, "message": e.message})
    return _delivery_view(delivery)


@router.post("/deliveries/{delivery_id}/handoff", response_model=DeliveryView)
def verify_handoff(
    delivery_id: str,
    payload: HandoffVerifyRequest,
    db: Session = Depends(get_db),
    _staff: models.StaffUser = Depends(require_platform_admin),
):
    delivery = db.query(models.Delivery).filter_by(id=delivery_id).first()
    if delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found.")
    try:
        delivery = mark_handoff_verified(db, delivery=delivery, verified=payload.verified, reason=payload.reason)
    except DeliveryError as e:
        raise HTTPException(status_code=422, detail={"code": e.code, "message": e.message})
    return _delivery_view(delivery)


def _delivery_view(d: models.Delivery) -> DeliveryView:
    return DeliveryView(
        id=d.id,
        order_id=d.order_id,
        status=d.status.value,
        eta_min_minutes=d.eta_min_minutes,
        eta_max_minutes=d.eta_max_minutes,
        handoff_verified=d.handoff_verified,
        failure_reason=d.failure_reason,
    )
