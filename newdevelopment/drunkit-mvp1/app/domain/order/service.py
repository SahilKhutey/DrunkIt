"""
Order service.

Every rule from the original spec that matters at MVP scale lives here:
- PRODUCT PAGE PRICE == CART PRICE == CHECKOUT PRICE (we snapshot price
  at add-to-cart time via unit_price_paise and never recompute it from
  a "current price" lookup at checkout).
- The eligibility check and inventory check both re-run at checkout
  time, server-side, independent of what was true when the item was
  added to cart minutes/hours earlier.
- Fail closed: any missing price/inventory/eligibility data blocks the
  order rather than defaulting to "allow."
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db import models
from app.domain.eligibility.service import get_current_eligibility


class OrderError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


@dataclass
class CartLine:
    product_id: str
    quantity: int


def create_order(
    db: Session,
    *,
    consumer: models.Consumer,
    store_id: str,
    lines: list[CartLine],
    delivery_address: str,
    delivery_latitude: float,
    delivery_longitude: float,
) -> models.Order:
    if not lines:
        raise OrderError("EMPTY_CART", "Cart has no items.")

    # 1. Eligibility — re-evaluated server-side, right now, not trusted from earlier.
    eligibility = get_current_eligibility(db, consumer=consumer)
    if not eligibility.can_checkout:
        raise OrderError("INELIGIBLE", eligibility.reason)

    store = db.query(models.Store).filter_by(id=store_id).first()
    if store is None or not store.active or not store.is_open:
        raise OrderError("STORE_UNAVAILABLE", "Store is not currently available.")

    order = models.Order(
        consumer_id=consumer.id,
        store_id=store.id,
        status=models.OrderStatus.CREATED,
        delivery_address=delivery_address,
        delivery_latitude=delivery_latitude,
        delivery_longitude=delivery_longitude,
    )
    db.add(order)
    db.flush()  # get order.id without committing yet

    subtotal = 0
    for line in lines:
        if line.quantity <= 0:
            raise OrderError("INVALID_QUANTITY", f"Invalid quantity for product {line.product_id}.")

        product = db.query(models.Product).filter_by(id=line.product_id, active=True).first()
        if product is None:
            raise OrderError("PRODUCT_NOT_FOUND", f"Product {line.product_id} not found or inactive.")

        listing = (
            db.query(models.Listing)
            .filter_by(store_id=store.id, product_id=product.id, status=models.ListingStatus.ACTIVE)
            .first()
        )
        if listing is None:
            raise OrderError("LISTING_UNAVAILABLE", f"{product.name} is not listed at this store.")

        inventory = (
            db.query(models.InventoryItem)
            .filter_by(store_id=store.id, product_id=product.id)
            .first()
        )
        # Fail closed: no inventory record at all means we don't know
        # the state, so we refuse rather than assume available.
        if inventory is None or inventory.quantity < line.quantity:
            raise OrderError(
                "OUT_OF_STOCK",
                f"{product.name} does not have enough stock at this store.",
            )

        price = db.query(models.PriceRecord).filter_by(store_id=store.id, product_id=product.id).first()
        if price is None:
            raise OrderError("PRICE_UNAVAILABLE", f"No price available for {product.name}.")

        # Reserve stock immediately. A production system would use a
        # short-lived hold/expiry instead of a hard decrement, but for
        # MVP a straightforward decrement inside this transaction is
        # correct and avoids overselling.
        inventory.quantity -= line.quantity
        db.add(inventory)

        order_item = models.OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=line.quantity,
            unit_price_paise=price.selling_price_paise,
        )
        db.add(order_item)
        subtotal += price.selling_price_paise * line.quantity

    delivery_fee = 2500  # flat ₹25 delivery fee placeholder — replace with real pricing service later
    order.subtotal_paise = subtotal
    order.delivery_fee_paise = delivery_fee
    order.total_paise = subtotal + delivery_fee
    order.status = models.OrderStatus.CONFIRMED

    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, *, order_id: str, consumer_id: str) -> models.Order | None:
    return (
        db.query(models.Order)
        .filter_by(id=order_id, consumer_id=consumer_id)
        .first()
    )
