"""Order REST API routes."""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_platform.config.settings import get_settings
from faccp_platform.database.session import get_db_session
from ...domain.exceptions import ComplianceCheckFailedError
from ...repositories.order import OrderRepository
from ...schemas.order import CreateOrderRequest, OrderItemResponse, OrderResponse
from ...services.compliance_client import ComplianceClient
from ...services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    request: CreateOrderRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Create a new compliance-gated, idempotent Order."""
    settings = get_settings()
    compliance_url = getattr(settings, "COMPLIANCE_URL", "http://localhost:8011")
    compliance_client = ComplianceClient(base_url=compliance_url)
    service = OrderService(session=session, compliance_client=compliance_client)

    try:
        order = await service.create_order(request)
        await session.commit()
        await session.refresh(order)

        order_repo = OrderRepository(session)
        items = await order_repo.get_items(order.id)
        item_responses = [OrderItemResponse.model_validate(i) for i in items]

        resp = OrderResponse.model_validate(order)
        resp.items = item_responses
        return resp
    except ComplianceCheckFailedError as exc:
        await session.commit()  # Commit failed order record in COMPLIANCE_FAILED state
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
async def get_order(
    order_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch order by order_id."""
    order_repo = OrderRepository(session)
    order = await order_repo.get(order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    items = await order_repo.get_items(order_id)
    item_responses = [OrderItemResponse.model_validate(i) for i in items]

    resp = OrderResponse.model_validate(order)
    resp.items = item_responses
    return resp
