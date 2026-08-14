"""Saga Orchestrator logic and compensation engine."""

from __future__ import annotations

import logging
import uuid
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_platform.events.envelope import EventEnvelope
from faccp_platform.events.outbox import enqueue_event
from faccp_platform.events.topics import Topics
from .enums import SagaState
from .models import SagaInstance

logger = logging.getLogger("faccp.saga.orchestrator")


def _get_aggregate_id(event: Any) -> str:
    if isinstance(event, dict):
        return str(event.get("aggregate_id") or event.get("order_id") or "")
    return str(getattr(event, "aggregate_id", getattr(event, "order_id", "")))


class OrderSaga:
    """Order Saga Orchestrator managing distributed forward workflow and compensation logic."""

    def __init__(self, session: AsyncSession | None = None, publisher: Any | None = None) -> None:
        self.session = session
        self.publisher = publisher

    async def get_or_create_saga(self, order_id: str | uuid.UUID) -> SagaInstance:
        oid_str = str(order_id)
        if self.session is None:
            return SagaInstance(order_id=oid_str, state=SagaState.CREATED)

        stmt = select(SagaInstance).where(SagaInstance.order_id == oid_str)
        res = await self.session.execute(stmt)
        saga = res.scalar_one_or_none()
        if not saga:
            saga = SagaInstance(order_id=oid_str, state=SagaState.CREATED)
            self.session.add(saga)
            await self.session.flush()
        return saga

    async def publish(self, topic: str, event_type: str, aggregate_id: str | uuid.UUID, payload: dict[str, Any]) -> None:
        agg_str = str(aggregate_id)
        if self.session is not None:
            await enqueue_event(
                self.session,
                topic=topic,
                event_type=event_type,
                aggregate_id=agg_str,
                payload=payload,
            )
        if self.publisher is not None:
            try:
                await self.publisher.publish(topic, payload, key=agg_str)
            except Exception as exc:
                logger.warning(f"Saga direct publish warning: {exc}")

    async def handle(self, event: Any) -> None:
        """Route event to corresponding saga handler."""
        event_type = getattr(event, "event_type", None)
        if event_type is None and isinstance(event, dict):
            event_type = event.get("event_type")

        if event_type in (Topics.ORDER_CREATED, "order.created"):
            await self.on_order_created(event)
        elif event_type in (Topics.COMPLIANCE_APPROVED, "compliance.approved"):
            await self.on_compliance_approved(event)
        elif event_type in (Topics.RISK_APPROVED, "risk.approved"):
            await self.on_risk_approved(event)
        elif event_type in (Topics.PAYMENT_CAPTURED, "payment.captured"):
            await self.on_payment_captured(event)
        elif event_type in (Topics.INVENTORY_RESERVED, "inventory.reserved"):
            await self.on_inventory_reserved(event)
        elif event_type in (Topics.FULFILLMENT_READY, "fulfillment.ready"):
            await self.on_fulfillment_ready(event)
        elif event_type in (Topics.DELIVERY_ARRIVED, "delivery.arrived"):
            await self.on_delivery_arrived(event)
        elif event_type in (Topics.VERIFICATION_COMPLETED, "verification.completed"):
            await self.on_verification_completed(event)
        elif event_type in (Topics.INVENTORY_FAILED, "inventory.failed"):
            await self.on_inventory_failed(event)
        elif event_type in (Topics.PAYMENT_REFUNDED, "payment.refunded"):
            await self.on_payment_refunded(event)

    # Forward Handlers
    async def on_order_created(self, event: Any) -> None:
        agg_id = _get_aggregate_id(event)
        saga = await self.get_or_create_saga(agg_id)
        saga.state = SagaState.COMPLIANCE_PENDING
        await self.publish(
            Topics.COMPLIANCE_CHECK_REQUESTED,
            Topics.COMPLIANCE_CHECK_REQUESTED,
            agg_id,
            {"order_id": str(agg_id)},
        )

    async def on_compliance_approved(self, event: Any) -> None:
        agg_id = _get_aggregate_id(event)
        saga = await self.get_or_create_saga(agg_id)
        saga.state = SagaState.RISK_PENDING
        await self.publish(
            Topics.RISK_CHECK_REQUESTED,
            Topics.RISK_CHECK_REQUESTED,
            agg_id,
            {"order_id": str(agg_id)},
        )

    async def on_risk_approved(self, event: Any) -> None:
        agg_id = _get_aggregate_id(event)
        saga = await self.get_or_create_saga(agg_id)
        saga.state = SagaState.PAYMENT_PENDING
        await self.publish(
            Topics.PAYMENT_AUTHORIZATION_REQUESTED,
            Topics.PAYMENT_AUTHORIZATION_REQUESTED,
            agg_id,
            {"order_id": str(agg_id)},
        )

    async def on_payment_captured(self, event: Any) -> None:
        agg_id = _get_aggregate_id(event)
        saga = await self.get_or_create_saga(agg_id)
        saga.state = SagaState.INVENTORY_PENDING
        await self.publish(
            Topics.INVENTORY_RESERVATION_REQUESTED,
            Topics.INVENTORY_RESERVATION_REQUESTED,
            agg_id,
            {"order_id": str(agg_id)},
        )

    async def on_inventory_reserved(self, event: Any) -> None:
        agg_id = _get_aggregate_id(event)
        saga = await self.get_or_create_saga(agg_id)
        saga.state = SagaState.FULFILLMENT_PENDING
        await self.publish(
            Topics.FULFILLMENT_REQUESTED,
            Topics.FULFILLMENT_REQUESTED,
            agg_id,
            {"order_id": str(agg_id)},
        )

    async def on_fulfillment_ready(self, event: Any) -> None:
        agg_id = _get_aggregate_id(event)
        saga = await self.get_or_create_saga(agg_id)
        saga.state = SagaState.DELIVERY_PENDING
        await self.publish(
            Topics.DELIVERY_REQUESTED,
            Topics.DELIVERY_REQUESTED,
            agg_id,
            {"order_id": str(agg_id)},
        )

    async def on_delivery_arrived(self, event: Any) -> None:
        agg_id = _get_aggregate_id(event)
        saga = await self.get_or_create_saga(agg_id)
        saga.state = SagaState.VERIFICATION_PENDING
        await self.publish(
            Topics.VERIFICATION_STARTED,
            Topics.VERIFICATION_STARTED,
            agg_id,
            {"order_id": str(agg_id)},
        )

    async def on_verification_completed(self, event: Any) -> None:
        agg_id = _get_aggregate_id(event)
        status = event.get("status") if isinstance(event, dict) else getattr(event, "status", "passed")
        if status in ("passed", "PASSED"):
            saga = await self.get_or_create_saga(agg_id)
            saga.state = SagaState.COMPLETED
            await self.publish(
                Topics.ORDER_COMPLETED,
                Topics.ORDER_COMPLETED,
                agg_id,
                {"order_id": str(agg_id), "status": "completed"},
            )
        else:
            await self.on_verification_failed(event)

    # Compensation Handlers
    async def on_inventory_failed(self, event: Any) -> None:
        agg_id = _get_aggregate_id(event)
        saga = await self.get_or_create_saga(agg_id)
        saga.state = SagaState.COMPENSATING
        logger.info(f"Inventory failed for order {agg_id}. Compensating via payment refund.")
        await self.publish(
            Topics.PAYMENT_REFUND_REQUESTED,
            Topics.PAYMENT_REFUND_REQUESTED,
            agg_id,
            {"order_id": str(agg_id), "reason": "inventory_unavailable"},
        )

    async def on_verification_failed(self, event: Any) -> None:
        agg_id = _get_aggregate_id(event)
        saga = await self.get_or_create_saga(agg_id)
        saga.state = SagaState.COMPENSATING
        logger.info(f"Verification failed for order {agg_id}. Compensating via delivery return and refund.")
        await self.publish(
            Topics.PAYMENT_REFUND_REQUESTED,
            Topics.PAYMENT_REFUND_REQUESTED,
            agg_id,
            {"order_id": str(agg_id), "reason": "verification_failed"},
        )

    async def on_payment_refunded(self, event: Any) -> None:
        agg_id = _get_aggregate_id(event)
        saga = await self.get_or_create_saga(agg_id)
        saga.state = SagaState.FAILED
        await self.publish(
            Topics.ORDER_CANCELLED,
            Topics.ORDER_CANCELLED,
            agg_id,
            {"order_id": str(agg_id), "reason": "compensated_and_cancelled"},
        )
