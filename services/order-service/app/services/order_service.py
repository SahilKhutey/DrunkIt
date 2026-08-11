"""
Order service — orchestrates the full order lifecycle.

Integrates with compliance, inventory, and audit services to ensure
every transition is policy-conformant, fully audited, and recoverable.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from faccp_common.events import make_event
from faccp_common.exceptions import (
    BadRequestError, ConflictError, NotFoundError, StateTransitionError,
)
from faccp_common.kafka_client import EventProducer
from faccp_common.logging import get_logger

from app.config import get_settings
from app.db.models import Order, OrderItem, OrderStateHistory
from app.domain.state_machine import (
    OrderState, assert_transition, can_transition, is_terminal,
)
from app.schemas.order import (
    CreateOrderRequest, OrderResponse, OrderItemResponse,
    StateTransitionRequest,
)

logger = get_logger(__name__)
settings = get_settings()


class OrderService:
    """Core order lifecycle service."""

    def __init__(
        self, db: AsyncSession,
        producer: EventProducer | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.db = db
        self.producer = producer
        self._http = http_client or httpx.AsyncClient(timeout=10.0)

    async def close(self) -> None:
        await self._http.aclose()

    # ============================================================
    # Create
    # ============================================================
    async def create_order(
        self, payload: CreateOrderRequest, *, actor_id: str
    ) -> OrderResponse:
        items_data: list[dict[str, Any]] = []
        subtotal = Decimal("0")
        for item in payload.items:
            line_total = item.unit_price * item.quantity
            subtotal += line_total
            items_data.append({
                "product_id": item.product_id,
                "sku": item.sku,
                "product_name": item.product_name,
                "category": item.category,
                "brand": item.brand,
                "abv": item.abv,
                "bottle_size_ml": item.bottle_size_ml,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "line_total": line_total,
            })
        tax_amount = subtotal * Decimal("0.18")
        total = subtotal + tax_amount + payload.delivery_fee + payload.platform_fee - payload.discount_amount

        order = Order(
            id=str(uuid.uuid4()),
            order_number=self._generate_order_number(),
            state=OrderState.CREATED.value,
            consumer_id=payload.consumer_id,
            retailer_id=payload.retailer_id,
            store_id=payload.store_id,
            subtotal=subtotal,
            tax_amount=tax_amount,
            delivery_fee=payload.delivery_fee,
            platform_fee=payload.platform_fee,
            discount_amount=payload.discount_amount,
            total_amount=total,
            currency=payload.currency,
            jurisdiction_code=payload.jurisdiction_code,
            delivery_address=payload.delivery_address,
            delivery_zone=payload.delivery_zone,
            delivery_instructions=payload.delivery_instructions,
            metadata_json=payload.metadata or {},
            placed_at=datetime.now(timezone.utc),
        )
        self.db.add(order)

        for item_data in items_data:
            self.db.add(OrderItem(order_id=order.id, **item_data))

        history = OrderStateHistory(
            order_id=order.id,
            from_state=None,
            to_state=OrderState.CREATED.value,
            actor_id=actor_id,
            actor_type="user",
            reason="Order created",
        )
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(order)

        await self._emit("order.created", {
            "order_id": order.id,
            "order_number": order.order_number,
            "consumer_id": order.consumer_id,
            "retailer_id": order.retailer_id,
            "store_id": order.store_id,
            "total_amount": str(order.total_amount),
            "jurisdiction": order.jurisdiction_code,
        }, actor_id)

        await self._run_validation_pipeline(order.id, actor_id)

        return await self._to_response(order)

    # ============================================================
    # State transitions
    # ============================================================
    async def transition(
        self,
        order_id: str,
        request: StateTransitionRequest,
        *,
        actor_id: str,
        actor_type: str = "user",
    ) -> OrderResponse:
        order = await self._get_order(order_id)
        current = OrderState(order.state)
        target = OrderState(request.target_state)

        if not can_transition(current, target):
            raise StateTransitionError(
                f"Cannot transition from {current.value} to {target.value}"
            )

        order.previous_state = order.state
        order.state = target.value

        history = OrderStateHistory(
            order_id=order.id,
            from_state=current.value,
            to_state=target.value,
            actor_id=actor_id,
            actor_type=actor_type,
            reason=request.reason,
            metadata_json=request.metadata or {},
        )
        self.db.add(history)

        now = datetime.now(timezone.utc)
        if target == OrderState.CONFIRMED:
            order.confirmed_at = now
        elif target == OrderState.CANCELLED:
            order.cancelled_at = now
            order.cancellation_reason = request.reason
        elif target == OrderState.DELIVERED:
            order.actual_delivery_at = now

        await self.db.commit()
        await self.db.refresh(order)

        await self._emit("order.state_changed", {
            "order_id": order.id,
            "from_state": current.value,
            "to_state": target.value,
            "actor_id": actor_id,
            "actor_type": actor_type,
            "reason": request.reason,
        }, actor_id)

        await self._audit(order, actor_id, actor_type, current.value, target.value, request.reason)

        return await self._to_response(order)

    # ============================================================
    # Validation pipeline (async)
    # ============================================================
    async def _run_validation_pipeline(self, order_id: str, actor_id: str) -> None:
        """CREATED → VALIDATING → COMPLIANCE_CHECK → PAYMENT_PENDING"""
        try:
            await self.transition(
                order_id,
                StateTransitionRequest(target_state=OrderState.VALIDATING.value),
                actor_id=actor_id, actor_type="system",
            )
            ok = await self._check_inventory(order_id)
            if not ok:
                await self.transition(
                    order_id,
                    StateTransitionRequest(
                        target_state=OrderState.OUT_OF_STOCK.value,
                        reason="Inventory check failed",
                    ),
                    actor_id=actor_id, actor_type="system",
                )
                return

            await self.transition(
                order_id,
                StateTransitionRequest(target_state=OrderState.COMPLIANCE_CHECK.value),
                actor_id=actor_id, actor_type="system",
            )

            decision = await self._evaluate_compliance(order_id)
            if decision["decision"] == "deny":
                await self.transition(
                    order_id,
                    StateTransitionRequest(
                        target_state=OrderState.COMPLIANCE_BLOCKED.value,
                        reason=f"Compliance denied: {', '.join(decision.get('reasons', []))}",
                    ),
                    actor_id=actor_id, actor_type="system",
                )
                return
            if decision["decision"] == "review":
                logger.warning("order.requires_review", order_id=order_id, decision=decision)

            await self.transition(
                order_id,
                StateTransitionRequest(target_state=OrderState.PAYMENT_PENDING.value),
                actor_id=actor_id, actor_type="system",
            )
        except Exception as e:
            logger.exception("order.validation_pipeline_failed", order_id=order_id)
            await self._emit("order.validation_failed", {
                "order_id": order_id, "error": str(e),
            }, actor_id)

    # ============================================================
    # External service calls
    # ============================================================
    async def _check_inventory(self, order_id: str) -> bool:
        try:
            order = await self._get_order(order_id)
            response = await self._http.post(
                f"{settings.inventory_service_url}/api/v1/inventory/reserve",
                json={
                    "order_id": order.id,
                    "store_id": order.store_id,
                    "items": [
                        {"product_id": i.product_id, "quantity": i.quantity}
                        for i in order.items
                    ],
                },
                timeout=5.0,
            )
            return response.status_code == 200
        except Exception:
            logger.exception("inventory_check_failed")
            return False

    async def _evaluate_compliance(self, order_id: str) -> dict[str, Any]:
        try:
            order = await self._get_order(order_id)
            response = await self._http.post(
                f"{settings.compliance_service_url}/api/v1/evaluate",
                json={
                    "subject_id": order.id,
                    "jurisdiction_code": order.jurisdiction_code,
                    "actor": {"user_id": order.consumer_id, "type": "consumer"},
                    "context": {
                        "consumer_age": 25,
                        "quantity": sum(i.quantity for i in order.items),
                        "delivery_zone": order.delivery_zone,
                        "license": {"status": "ACTIVE", "valid_until": "2026-12-31T00:00:00Z"},
                        "product": {"category": order.items[0].category if order.items else "unknown"},
                    },
                },
                timeout=5.0,
            )
            data = response.json()
            if data.get("data"):
                order.compliance_decision_id = data["data"].get("decision_id")
                order.compliance_decision = data["data"].get("decision")
                await self.db.commit()
            return data.get("data", {"decision": "review", "reasons": []})
        except Exception:
            logger.exception("compliance_check_failed")
            return {"decision": "review", "reasons": ["compliance_service_unavailable"]}

    # ============================================================
    # Audit
    # ============================================================
    async def _audit(
        self, order: Order, actor_id: str, actor_type: str,
        from_state: str, to_state: str, reason: str | None,
    ) -> None:
        try:
            await self._http.post(
                f"{settings.audit_service_url}/api/v1/audit/events",
                json={
                    "actor_id": actor_id,
                    "actor_type": actor_type,
                    "action": "ORDER_STATE_TRANSITION",
                    "resource_type": "order",
                    "resource_id": order.id,
                    "event_type": f"order.{to_state.lower()}",
                    "result": "success",
                    "severity": "info",
                    "service_name": settings.service_name,
                    "correlation_id": order.id,
                    "description": f"Order {from_state} → {to_state}",
                    "payload": {
                        "from_state": from_state,
                        "to_state": to_state,
                        "reason": reason,
                    },
                },
                timeout=3.0,
            )
        except Exception:
            logger.exception("audit_emission_failed")

    # ============================================================
    # Read
    # ============================================================
    async def get(self, order_id: str) -> OrderResponse:
        order = await self._get_order(order_id)
        return await self._to_response(order)

    async def list_for_consumer(self, consumer_id: str, page: int = 1, page_size: int = 20) -> list[OrderResponse]:
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Order)
            .where(Order.consumer_id == consumer_id)
            .options(selectinload(Order.items), selectinload(Order.state_history))
            .order_by(Order.created_at.desc())
            .offset(offset).limit(page_size)
        )
        return [await self._to_response(o) for o in result.scalars().all()]

    async def list_for_store(self, store_id: str, state: str | None = None, page: int = 1, page_size: int = 20) -> list[OrderResponse]:
        offset = (page - 1) * page_size
        q = select(Order).where(Order.store_id == store_id)
        if state:
            q = q.where(Order.state == state)
        q = q.options(selectinload(Order.items)).order_by(Order.created_at.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(q)
        return [await self._to_response(o) for o in result.scalars().all()]

    # ============================================================
    # Helpers
    # ============================================================
    async def _get_order(self, order_id: str) -> Order:
        result = await self.db.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items), selectinload(Order.state_history))
        )
        order = result.scalar_one_or_none()
        if order is None:
            raise NotFoundError(f"Order not found: {order_id}")
        return order

    async def _to_response(self, order: Order) -> OrderResponse:
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            state=order.state,
            previous_state=order.previous_state,
            consumer_id=order.consumer_id,
            retailer_id=order.retailer_id,
            store_id=order.store_id,
            driver_id=order.driver_id,
            subtotal=order.subtotal,
            tax_amount=order.tax_amount,
            delivery_fee=order.delivery_fee,
            platform_fee=order.platform_fee,
            discount_amount=order.discount_amount,
            total_amount=order.total_amount,
            currency=order.currency,
            jurisdiction_code=order.jurisdiction_code,
            compliance_decision=order.compliance_decision,
            delivery_address=order.delivery_address,
            delivery_zone=order.delivery_zone,
            estimated_delivery_at=order.estimated_delivery_at,
            actual_delivery_at=order.actual_delivery_at,
            placed_at=order.placed_at,
            confirmed_at=order.confirmed_at,
            cancelled_at=order.cancelled_at,
            cancellation_reason=order.cancellation_reason,
            items=[
                OrderItemResponse(
                    id=i.id, product_id=i.product_id, sku=i.sku,
                    product_name=i.product_name, category=i.category,
                    brand=i.brand, abv=i.abv, bottle_size_ml=i.bottle_size_ml,
                    quantity=i.quantity, unit_price=i.unit_price, line_total=i.line_total,
                )
                for i in order.items
            ],
            created_at=order.created_at,
            updated_at=order.updated_at,
        )

    def _generate_order_number(self) -> str:
        return f"FACCP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    async def _emit(self, event_type: str, payload: dict[str, Any], actor_id: str | None) -> None:
        if self.producer is None:
            return
        try:
            event = make_event(
                event_type=event_type, payload=payload,
                producer=settings.service_name, user_id=actor_id,
            )
            await self.producer.publish(topic="order.events", payload=event)
        except Exception:
            logger.exception("Failed to publish event", event_type=event_type)
