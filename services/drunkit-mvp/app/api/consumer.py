from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_consumer, get_optional_consumer
from app.db import models
from app.db.session import get_db
from app.domain.delivery.service import create_delivery_for_order
from app.domain.eligibility.service import get_current_eligibility, verify_consumer_eligibility
from app.domain.listing.service import get_listing_by_id, get_nearby_listings
from app.domain.order.service import CartLine, OrderError, create_order
from app.schemas.schemas import (
    DeliveryView,
    EligibilityVerifyRequest,
    EligibilityVerifyResponse,
    ListingCardView,
    MeResponse,
    OrderCreateRequest,
    OrderItemView,
    OrderSummaryView,
    OrderView,
    PriceView,
)

router = APIRouter(prefix="/v1", tags=["consumer"])


# ---- Me / profile ----

@router.get("/me", response_model=MeResponse)
def get_me(
    consumer: models.Consumer = Depends(get_current_consumer),
    db: Session = Depends(get_db),
):
    eligibility = get_current_eligibility(db, consumer=consumer)
    return MeResponse(
        consumer_id=consumer.id,
        phone=consumer.phone,
        state=consumer.state,
        eligibility_state=consumer.eligibility_state.value,
        minimum_age_required=eligibility.minimum_age_required,
    )


# ---- Eligibility ----

@router.post("/eligibility/verify", response_model=EligibilityVerifyResponse)
def verify_eligibility(
    payload: EligibilityVerifyRequest,
    consumer: models.Consumer = Depends(get_current_consumer),
    db: Session = Depends(get_db),
):
    result = verify_consumer_eligibility(
        db,
        consumer=consumer,
        state_key=payload.state,
        date_of_birth=payload.date_of_birth,
    )
    return EligibilityVerifyResponse(
        decision=result.decision,
        can_view=result.can_view,
        can_add_to_cart=result.can_add_to_cart,
        can_checkout=result.can_checkout,
        reason=result.reason,
        minimum_age_required=result.minimum_age_required,
        state=result.state_key,
    )


# ---- Listings ----

def _to_card(view) -> ListingCardView:
    return ListingCardView(
        listing_id=view.listing_id,
        product_id=view.product_id,
        name=view.name,
        brand=view.brand,
        category=view.category,
        variant=view.variant,
        pack_size=view.pack_size,
        image_url=view.image_url,
        price=PriceView(
            mrp=view.mrp_paise / 100,
            selling_price=view.selling_price_paise / 100,
            discount_percentage=view.discount_percentage,
        ),
        availability_status=view.availability_status,
        store_id=view.store_id,
        store_name=view.store_name,
        eta_min_minutes=view.eta_min_minutes,
        eta_max_minutes=view.eta_max_minutes,
        seller_verified=view.seller_verified,
        can_view=view.can_view,
        can_add_to_cart=view.can_add_to_cart,
        eligibility_reason=view.eligibility_reason,
    )


@router.get("/listings", response_model=list[ListingCardView])
def list_listings(
    lat: float = Query(...),
    lng: float = Query(...),
    state: str = Query(..., description="Delivery jurisdiction, e.g. MAHARASHTRA"),
    category: str | None = Query(None),
    consumer: models.Consumer | None = Depends(get_optional_consumer),
    db: Session = Depends(get_db),
):
    views = get_nearby_listings(
        db, latitude=lat, longitude=lng, state_key=state, consumer=consumer, category=category
    )
    return [_to_card(v) for v in views]


@router.get("/listings/{listing_id}", response_model=ListingCardView)
def get_listing(
    listing_id: str,
    consumer: models.Consumer | None = Depends(get_optional_consumer),
    db: Session = Depends(get_db),
):
    view = get_listing_by_id(db, listing_id=listing_id, consumer=consumer)
    if view is None:
        raise HTTPException(status_code=404, detail="Listing not found or unavailable.")
    return _to_card(view)


# ---- Orders ----

def _order_to_view(order: models.Order) -> OrderView:
    return OrderView(
        id=order.id,
        status=order.status.value,
        subtotal=order.subtotal_paise / 100,
        delivery_fee=order.delivery_fee_paise / 100,
        total=order.total_paise / 100,
        items=[
            OrderItemView(
                product_id=item.product_id,
                product_name=item.product.name,
                quantity=item.quantity,
                unit_price=item.unit_price_paise / 100,
            )
            for item in order.items
        ],
    )


@router.post("/orders", response_model=OrderView)
def place_order(
    payload: OrderCreateRequest,
    consumer: models.Consumer = Depends(get_current_consumer),
    db: Session = Depends(get_db),
):
    try:
        order = create_order(
            db,
            consumer=consumer,
            store_id=payload.store_id,
            lines=[CartLine(product_id=i.product_id, quantity=i.quantity) for i in payload.items],
            delivery_address=payload.delivery_address,
            delivery_latitude=payload.delivery_latitude,
            delivery_longitude=payload.delivery_longitude,
        )
    except OrderError as e:
        raise HTTPException(status_code=422, detail={"code": e.code, "message": e.message})

    create_delivery_for_order(db, order=order)
    db.refresh(order)
    return _order_to_view(order)


@router.get("/orders", response_model=list[OrderSummaryView])
def list_my_orders(
    consumer: models.Consumer = Depends(get_current_consumer),
    db: Session = Depends(get_db),
):
    orders = (
        db.query(models.Order)
        .filter_by(consumer_id=consumer.id)
        .order_by(models.Order.created_at.desc())
        .all()
    )
    return [
        OrderSummaryView(
            id=o.id,
            status=o.status.value,
            total=o.total_paise / 100,
            item_count=sum(i.quantity for i in o.items),
            created_at=o.created_at.isoformat(),
        )
        for o in orders
    ]


@router.get("/orders/{order_id}", response_model=OrderView)
def get_order_view(
    order_id: str,
    consumer: models.Consumer = Depends(get_current_consumer),
    db: Session = Depends(get_db),
):
    order = db.query(models.Order).filter_by(id=order_id, consumer_id=consumer.id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found.")
    return _order_to_view(order)


# ---- Delivery tracking (consumer read-only) ----

@router.get("/orders/{order_id}/delivery", response_model=DeliveryView)
def get_order_delivery(
    order_id: str,
    consumer: models.Consumer = Depends(get_current_consumer),
    db: Session = Depends(get_db),
):
    order = db.query(models.Order).filter_by(id=order_id, consumer_id=consumer.id).first()
    if order is None or order.delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found.")
    d = order.delivery
    return DeliveryView(
        id=d.id,
        order_id=d.order_id,
        status=d.status.value,
        eta_min_minutes=d.eta_min_minutes,
        eta_max_minutes=d.eta_max_minutes,
        handoff_verified=d.handoff_verified,
        failure_reason=d.failure_reason,
    )
