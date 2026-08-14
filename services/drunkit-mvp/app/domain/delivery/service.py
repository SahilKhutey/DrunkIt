"""
Delivery service (MVP slice).

Intentionally NOT a full dispatch/routing/tracking engine — for v1,
drivers are assigned manually by a store/ops person via the admin API,
and location tracking is out of scope. What we do keep from the
original spec, because it's the part that actually matters for a
regulated product, is:

  1. Delivery as an explicit state machine, separate from Order status.
  2. A mandatory HANDOFF_VERIFICATION state before DELIVERED — the
     system cannot silently skip from IN_TRANSIT to DELIVERED without
     an explicit verification step being recorded.
  3. An append-only event log for every transition (audit trail).
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import models

settings = get_settings()

_ALLOWED_TRANSITIONS: dict[models.DeliveryStatus, set[models.DeliveryStatus]] = {
    models.DeliveryStatus.REQUESTED: {models.DeliveryStatus.ASSIGNED, models.DeliveryStatus.CANCELLED},
    models.DeliveryStatus.ASSIGNED: {models.DeliveryStatus.PICKED_UP, models.DeliveryStatus.CANCELLED},
    models.DeliveryStatus.PICKED_UP: {models.DeliveryStatus.IN_TRANSIT, models.DeliveryStatus.FAILED},
    models.DeliveryStatus.IN_TRANSIT: {models.DeliveryStatus.ARRIVING, models.DeliveryStatus.FAILED},
    models.DeliveryStatus.ARRIVING: {models.DeliveryStatus.HANDOFF_VERIFICATION, models.DeliveryStatus.FAILED},
    models.DeliveryStatus.HANDOFF_VERIFICATION: {models.DeliveryStatus.DELIVERED, models.DeliveryStatus.FAILED},
    models.DeliveryStatus.DELIVERED: set(),
    models.DeliveryStatus.FAILED: set(),
    models.DeliveryStatus.CANCELLED: set(),
}


class DeliveryError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def create_delivery_for_order(db: Session, *, order: models.Order) -> models.Delivery:
    delivery = models.Delivery(
        order_id=order.id,
        status=models.DeliveryStatus.REQUESTED,
        eta_min_minutes=settings.default_eta_min_minutes,
        eta_max_minutes=settings.default_eta_max_minutes,
    )
    db.add(delivery)
    db.flush()
    _log_event(db, delivery.id, "DELIVERY_REQUESTED", None)
    db.commit()
    db.refresh(delivery)
    return delivery


def _log_event(db: Session, delivery_id: str, event_type: str, detail: str | None) -> None:
    db.add(models.DeliveryEvent(delivery_id=delivery_id, event_type=event_type, detail=detail))


def transition(
    db: Session,
    *,
    delivery: models.Delivery,
    new_status: models.DeliveryStatus,
    detail: str | None = None,
) -> models.Delivery:
    allowed = _ALLOWED_TRANSITIONS.get(delivery.status, set())
    if new_status not in allowed:
        raise DeliveryError(
            "INVALID_TRANSITION",
            f"Cannot move delivery from {delivery.status.value} to {new_status.value}.",
        )

    delivery.status = new_status
    if new_status == models.DeliveryStatus.DELIVERED:
        delivery.handoff_verified = True
    if new_status == models.DeliveryStatus.FAILED and detail:
        delivery.failure_reason = detail

    db.add(delivery)
    _log_event(db, delivery.id, new_status.value, detail)

    # Keep the parent order status roughly in sync for the consumer view.
    order = delivery.order
    order_status_map = {
        models.DeliveryStatus.PICKED_UP: models.OrderStatus.OUT_FOR_DELIVERY,
        models.DeliveryStatus.IN_TRANSIT: models.OrderStatus.OUT_FOR_DELIVERY,
        models.DeliveryStatus.ARRIVING: models.OrderStatus.OUT_FOR_DELIVERY,
        models.DeliveryStatus.DELIVERED: models.OrderStatus.DELIVERED,
        models.DeliveryStatus.FAILED: models.OrderStatus.FAILED,
        models.DeliveryStatus.CANCELLED: models.OrderStatus.CANCELLED,
    }
    if new_status in order_status_map:
        order.status = order_status_map[new_status]
        db.add(order)

    db.commit()
    db.refresh(delivery)
    return delivery


def mark_handoff_verified(
    db: Session,
    *,
    delivery: models.Delivery,
    verified: bool,
    reason: str | None = None,
) -> models.Delivery:
    """
    Called by the driver app at the doorstep. This is the controlled
    handoff gate: a delivery can only become DELIVERED by passing
    through this explicit check, never by skipping straight from
    ARRIVING. The actual verification method (ID scan, OTP, etc.) is
    intentionally out of scope for MVP and should be swapped in behind
    this function without changing the state machine.
    """
    if delivery.status != models.DeliveryStatus.HANDOFF_VERIFICATION:
        raise DeliveryError(
            "NOT_AT_HANDOFF_STAGE",
            f"Delivery must be in HANDOFF_VERIFICATION, currently {delivery.status.value}.",
        )

    if not verified:
        return transition(db, delivery=delivery, new_status=models.DeliveryStatus.FAILED, detail=reason or "Handoff verification failed.")

    return transition(db, delivery=delivery, new_status=models.DeliveryStatus.DELIVERED, detail="Handoff verified.")
