"""Cart REST API routes."""

from __future__ import annotations

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_platform.database.session import get_db_session
from ...repositories.cart import CartRepository
from ...schemas.cart import AddToCartRequest, CartItemResponse, CartResponse
from ...services.cart_service import CartService

router = APIRouter(prefix="/carts", tags=["carts"])


@router.post(
    "",
    response_model=CartResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_cart(
    consumer_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Create a new shopping cart."""
    service = CartService(session)
    cart = await service.create_cart(consumer_id)
    await session.commit()
    await session.refresh(cart)
    return CartResponse.model_validate(cart)


@router.post(
    "/{cart_id}/items",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_item(
    cart_id: uuid.UUID,
    request: AddToCartRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Add product item to cart."""
    service = CartService(session)
    item = await service.add_item(
        cart_id,
        request.product_id,
        request.quantity,
        request.unit_price,
    )
    await session.commit()
    await session.refresh(item)
    return CartItemResponse.model_validate(item)
