"""Order service routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.database import get_db
from faccp_common.dto import APIResponse, PaginatedResponse, paginated
from faccp_common.exceptions import UnauthorizedError
from faccp_common.kafka_client import EventProducer
from faccp_common.security import decode_token

from app.api.dependencies import get_order_service
from app.config import get_settings
from app.schemas.order import (
    CreateOrderRequest, OrderResponse, StateTransitionRequest,
)
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])
settings = get_settings()


def _extract_user_id(authorization: str | None) -> str:
    if not authorization:
        raise UnauthorizedError("Authentication required")
    try:
        token = authorization.replace("Bearer ", "").strip()
        claims = decode_token(
            token, secret=settings.jwt_secret, algorithm=settings.jwt_algorithm,
            issuer=settings.jwt_issuer, audience=settings.jwt_audience,
            expected_type="access",
        )
        return claims.get("sub", "unknown")
    except Exception as e:
        raise UnauthorizedError(f"Invalid token: {e}") from e


@router.post("", status_code=201)
async def create_order(
    payload: CreateOrderRequest,
    service: Annotated[OrderService, Depends(get_order_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> APIResponse[OrderResponse]:
    actor_id = _extract_user_id(authorization)
    order = await service.create_order(payload, actor_id=actor_id)
    return APIResponse(data=order, meta={"message": "Order created"})


@router.get("/{order_id}")
async def get_order(
    order_id: str,
    service: Annotated[OrderService, Depends(get_order_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> APIResponse[OrderResponse]:
    _extract_user_id(authorization)
    return APIResponse(data=await service.get(order_id))


@router.post("/{order_id}/transitions")
async def transition_order(
    order_id: str,
    payload: StateTransitionRequest,
    service: Annotated[OrderService, Depends(get_order_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> APIResponse[OrderResponse]:
    actor_id = _extract_user_id(authorization)
    order = await service.transition(order_id, payload, actor_id=actor_id)
    return APIResponse(data=order)


@router.get("/by-consumer/{consumer_id}")
async def list_for_consumer(
    consumer_id: str,
    service: Annotated[OrderService, Depends(get_order_service)],
    authorization: Annotated[str | None, Header()] = None,
    page: int = 1,
    page_size: int = 20,
) -> APIResponse[PaginatedResponse[OrderResponse]]:
    _extract_user_id(authorization)
    items = await service.list_for_consumer(consumer_id, page, page_size)
    return APIResponse(data=paginated(items, page, page_size, len(items)))


@router.get("/by-store/{store_id}")
async def list_for_store(
    store_id: str,
    service: Annotated[OrderService, Depends(get_order_service)],
    authorization: Annotated[str | None, Header()] = None,
    state: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> APIResponse[PaginatedResponse[OrderResponse]]:
    _extract_user_id(authorization)
    items = await service.list_for_store(store_id, state, page, page_size)
    return APIResponse(data=paginated(items, page, page_size, len(items)))
