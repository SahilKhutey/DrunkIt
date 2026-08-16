"""
Admin/ops API.

MVP-level authorization only: this router assumes it sits behind an
internal-only network boundary or a simple API-key middleware (see
main.py). Before any real launch, replace that with proper RBAC per
the original architecture's Admin/Retailer/Consumer separation.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import models
from app.db.session import get_db
from app.domain.delivery.service import DeliveryError, mark_handoff_verified, transition
from app.schemas.schemas import (
    DeliveryTransitionRequest,
    DeliveryView,
    HandoffVerifyRequest,
    ListingCreate,
    ProductCreate,
    RetailerCreate,
    StoreCreate,
)

router = APIRouter(prefix="/v1/admin", tags=["admin"])


@router.post("/retailers", response_model=dict)
def create_retailer(payload: RetailerCreate, db: Session = Depends(get_db)):
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
def verify_retailer(retailer_id: str, db: Session = Depends(get_db)):
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


@router.post("/stores", response_model=dict)
def create_store(payload: StoreCreate, db: Session = Depends(get_db)):
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


@router.post("/products", response_model=dict)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    product = models.Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return {"product_id": product.id}


@router.post("/listings", response_model=dict)
def create_listing(payload: ListingCreate, db: Session = Depends(get_db)):
    store = db.query(models.Store).filter_by(id=payload.store_id).first()
    product = db.query(models.Product).filter_by(id=payload.product_id).first()
    if store is None or product is None:
        raise HTTPException(status_code=404, detail="Store or product not found.")

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


# ---- Delivery ops (stand-in for a driver app) ----

@router.post("/deliveries/{delivery_id}/assign", response_model=DeliveryView)
def assign_driver(delivery_id: str, driver_name: str, driver_phone: str, db: Session = Depends(get_db)):
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
def transition_delivery(delivery_id: str, payload: DeliveryTransitionRequest, db: Session = Depends(get_db)):
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
def verify_handoff(delivery_id: str, payload: HandoffVerifyRequest, db: Session = Depends(get_db)):
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
