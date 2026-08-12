"""Order service: State Machine, Regulatory Lifecycle, Compliance Engine Integration."""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.communication.envelope import create_envelope
from faccp_common.communication.producer import EventProducer
from faccp_common.exceptions import BadRequestError, ConflictError, NotFoundError
from faccp_common.logging import get_logger

from app.db.models import (
    ComplianceValidationRecord, Order, OrderItem, OrderStateHistory,
)
from app.schemas.order import OrderCancelRequest, OrderCreate, OrderStateTransitionRequest

logger = get_logger(__name__)

# Regulatory Order State Machine Allowed Transitions
VALID_TRANSITIONS: dict[str, set[str]] = {
    "DRAFT": {"COMPLIANCE_PENDING", "CANCELLED"},
    "COMPLIANCE_PENDING": {"COMPLIANT", "CANCELLED"},
    "COMPLIANT": {"PAYMENT_PENDING", "CANCELLED"},
    "PAYMENT_PENDING": {"CONFIRMED", "CANCELLED"},
    "CONFIRMED": {"DISPATCH_PENDING", "CANCELLED"},
    "DISPATCH_PENDING": {"OUT_FOR_DELIVERY", "CANCELLED"},
    "OUT_FOR_DELIVERY": {"DELIVERED", "CANCELLED"},
    "DELIVERED": set(),
    "CANCELLED": set(),
}


def _generate_order_number() -> str:
    return f"ORD-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"


class OrderService:
    """Regulatory Order Lifecycle & Checkout Orchestrator."""

    def __init__(self, db: AsyncSession, producer: EventProducer | None = None) -> None:
        self.db = db
        self.producer = producer

    async def create_order(self, payload: OrderCreate) -> Order:
        order_num = _generate_order_number()
        total_amt = sum(item.unit_price_inr * item.quantity for item in payload.items)

        order = Order(
            order_number=order_num,
            consumer_id=payload.consumer_id,
            store_id=payload.store_id,
            delivery_address_id=payload.delivery_address_id,
            jurisdiction=payload.jurisdiction,
            order_state="DRAFT",
            total_amount_inr=total_amt,
            delivery_fee_inr=49.0,
            excise_tax_inr=0.0,
        )
        self.db.add(order)
        await self.db.flush()

        for item_in in payload.items:
            subtotal = item_in.unit_price_inr * item_in.quantity
            item = OrderItem(
                order_id=order.id,
                sku_id=item_in.sku_id,
                title=item_in.title,
                unit_price_inr=item_in.unit_price_inr,
                quantity=item_in.quantity,
                subtotal_inr=subtotal,
            )
            self.db.add(item)

        history = OrderStateHistory(
            order_id=order.id,
            from_state="NONE",
            to_state="DRAFT",
            triggered_by="checkout_engine",
            notes="Order draft created",
        )
        self.db.add(history)
        await self.db.commit()

        # Reload with items
        result = await self.db.execute(select(Order).where(Order.id == order.id))
        order = result.scalar_one()

        await self._publish("order.created", {
            "order_id": order.id, "order_number": order.order_number, "total_amount": order.total_amount_inr,
        })
        return order

    async def get_order(self, order_id: str) -> Order:
        result = await self.db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            raise NotFoundError(f"Order {order_id} not found")
        return order

    async def transition_state(
        self, order_id: str, payload: OrderStateTransitionRequest, actor_id: str = "order_engine"
    ) -> Order:
        order = await self.get_order(order_id)
        current = order.order_state
        target = payload.to_state.upper()

        allowed = VALID_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise BadRequestError(f"Invalid state transition from {current} to {target}. Allowed: {allowed}")

        order.order_state = target

        history = OrderStateHistory(
            order_id=order.id,
            from_state=current,
            to_state=target,
            triggered_by=actor_id,
            notes=payload.notes or f"Transitioned from {current} to {target}",
        )
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(order)

        await self._publish("order.state_changed", {
            "order_id": order.id, "from_state": current, "to_state": target, "actor_id": actor_id,
        })
        return order

    async def cancel_order(self, order_id: str, payload: OrderCancelRequest, actor_id: str = "user") -> Order:
        order = await self.get_order(order_id)
        if order.order_state in {"DELIVERED", "CANCELLED"}:
            raise BadRequestError(f"Cannot cancel order in state {order.order_state}")

        current = order.order_state
        order.order_state = "CANCELLED"
        order.cancellation_reason = payload.reason

        history = OrderStateHistory(
            order_id=order.id,
            from_state=current,
            to_state="CANCELLED",
            triggered_by=actor_id,
            notes=f"Cancelled: {payload.reason}",
        )
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(order)

        await self._publish("order.cancelled", {
            "order_id": order.id, "reason": payload.reason, "actor_id": actor_id,
        })
        return order

    async def _publish(self, event_type: str, payload: dict) -> None:
        if not self.producer:
            return
        try:
            envelope = create_envelope(event_type, payload, producer="faccp-order")
            await self.producer.publish("order.events", envelope)
        except Exception:
            logger.exception("event_publish_failed", event_type=event_type)
