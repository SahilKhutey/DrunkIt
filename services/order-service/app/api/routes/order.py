"""Order API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from faccp_common.dto import SuccessResponse

from app.api.dependencies import get_order_service
from app.schemas.order import (
    OrderCancelRequest, OrderCreate, OrderItemResponse, OrderResponse,
    OrderStateTransitionRequest,
)
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Regulatory Order Engine"])


@router.post("", response_model=SuccessResponse[OrderResponse], status_code=201)
async def create_order(
    payload: OrderCreate,
    service: Annotated[OrderService, Depends(get_order_service)],
) -> SuccessResponse[OrderResponse]:
    order = await service.create_order(payload)
    return SuccessResponse(data=OrderResponse(
        id=order.id, order_number=order.order_number, consumer_id=order.consumer_id,
        store_id=order.store_id, delivery_address_id=order.delivery_address_id,
        jurisdiction=order.jurisdiction, order_state=order.order_state,
        total_amount_inr=order.total_amount_inr, delivery_fee_inr=order.delivery_fee_inr,
        excise_tax_inr=order.excise_tax_inr, reservation_token=order.reservation_token,
        payment_intent_id=order.payment_intent_id, cancellation_reason=order.cancellation_reason,
        items=[OrderItemResponse(
            id=item.id, sku_id=item.sku_id, title=item.title,
            unit_price_inr=item.unit_price_inr, quantity=item.quantity, subtotal_inr=item.subtotal_inr,
        ) for item in order.items],
        created_at=order.created_at,
    ), message="Regulatory order draft created")


@router.get("/{order_id}", response_model=SuccessResponse[OrderResponse])
async def get_order(
    order_id: str,
    service: Annotated[OrderService, Depends(get_order_service)],
) -> SuccessResponse[OrderResponse]:
    order = await service.get_order(order_id)
    return SuccessResponse(data=OrderResponse(
        id=order.id, order_number=order.order_number, consumer_id=order.consumer_id,
        store_id=order.store_id, delivery_address_id=order.delivery_address_id,
        jurisdiction=order.jurisdiction, order_state=order.order_state,
        total_amount_inr=order.total_amount_inr, delivery_fee_inr=order.delivery_fee_inr,
        excise_tax_inr=order.excise_tax_inr, reservation_token=order.reservation_token,
        payment_intent_id=order.payment_intent_id, cancellation_reason=order.cancellation_reason,
        items=[OrderItemResponse(
            id=item.id, sku_id=item.sku_id, title=item.title,
            unit_price_inr=item.unit_price_inr, quantity=item.quantity, subtotal_inr=item.subtotal_inr,
        ) for item in order.items],
        created_at=order.created_at,
    ))


@router.post("/{order_id}/transition", response_model=SuccessResponse[OrderResponse])
async def transition_state(
    order_id: str,
    payload: OrderStateTransitionRequest,
    service: Annotated[OrderService, Depends(get_order_service)],
) -> SuccessResponse[OrderResponse]:
    order = await service.transition_state(order_id, payload)
    return SuccessResponse(data=OrderResponse(
        id=order.id, order_number=order.order_number, consumer_id=order.consumer_id,
        store_id=order.store_id, delivery_address_id=order.delivery_address_id,
        jurisdiction=order.jurisdiction, order_state=order.order_state,
        total_amount_inr=order.total_amount_inr, delivery_fee_inr=order.delivery_fee_inr,
        excise_tax_inr=order.excise_tax_inr, reservation_token=order.reservation_token,
        payment_intent_id=order.payment_intent_id, cancellation_reason=order.cancellation_reason,
        items=[OrderItemResponse(
            id=item.id, sku_id=item.sku_id, title=item.title,
            unit_price_inr=item.unit_price_inr, quantity=item.quantity, subtotal_inr=item.subtotal_inr,
        ) for item in order.items],
        created_at=order.created_at,
    ), message=f"Order state transitioned to {order.order_state}")


@router.post("/{order_id}/cancel", response_model=SuccessResponse[OrderResponse])
async def cancel_order(
    order_id: str,
    payload: OrderCancelRequest,
    service: Annotated[OrderService, Depends(get_order_service)],
) -> SuccessResponse[OrderResponse]:
    order = await service.cancel_order(order_id, payload)
    return SuccessResponse(data=OrderResponse(
        id=order.id, order_number=order.order_number, consumer_id=order.consumer_id,
        store_id=order.store_id, delivery_address_id=order.delivery_address_id,
        jurisdiction=order.jurisdiction, order_state=order.order_state,
        total_amount_inr=order.total_amount_inr, delivery_fee_inr=order.delivery_fee_inr,
        excise_tax_inr=order.excise_tax_inr, reservation_token=order.reservation_token,
        payment_intent_id=order.payment_intent_id, cancellation_reason=order.cancellation_reason,
        items=[OrderItemResponse(
            id=item.id, sku_id=item.sku_id, title=item.title,
            unit_price_inr=item.unit_price_inr, quantity=item.quantity, subtotal_inr=item.subtotal_inr,
        ) for item in order.items],
        created_at=order.created_at,
    ), message="Order cancelled")
