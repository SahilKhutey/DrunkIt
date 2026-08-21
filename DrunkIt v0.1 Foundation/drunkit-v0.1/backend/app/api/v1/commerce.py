"""Commerce API endpoints for Cart management, Compliance-Gated Checkout, and Orders."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_sync_db
from app.db.uow import SyncUnitOfWork
from app.models.identity import User
from app.schemas.commerce import (
    CartItemAdd,
    CartResponse,
    CheckoutRequest,
    OrderResponse,
)
from app.services.commerce_service import CommerceService

router = APIRouter(tags=["commerce"])


# ──────────────────────────────────────────────────────────────────────────────
# 1. Shopping Cart Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/cart",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Get active shopping cart",
)
def get_cart(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_sync_db),
) -> CartResponse:
    """Retrieve consumer's active shopping cart with calculated totals and formatted pricing."""
    cart = CommerceService.get_or_create_cart(current_user.id, session)
    return CommerceService.format_cart_response(cart, session)


@router.post(
    "/cart/items",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Add item to shopping cart",
)
def add_cart_item(
    request: CartItemAdd,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_sync_db),
) -> CartResponse:
    """Add a product variant SKU from a specific store location into the active cart."""
    uow = SyncUnitOfWork(session)
    with uow:
        cart_resp = CommerceService.add_item_to_cart(current_user.id, request, uow)
    return cart_resp


@router.delete(
    "/cart/items/{item_id}",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove item from shopping cart",
)
def remove_cart_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_sync_db),
) -> CartResponse:
    """Remove a specific line item from the active cart."""
    uow = SyncUnitOfWork(session)
    with uow:
        cart_resp = CommerceService.remove_item_from_cart(current_user.id, item_id, uow)
    return cart_resp


# ──────────────────────────────────────────────────────────────────────────────
# 2. Compliance-Gated Checkout Endpoint
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/cart/checkout",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Execute compliance-gated checkout",
)
def checkout_cart(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_sync_db),
) -> OrderResponse:
    """Execute atomic checkout: evaluates deterministic regulatory rules and converts cart to Confirmed Order."""
    uow = SyncUnitOfWork(session)
    with uow:
        order_resp = CommerceService.checkout_cart(current_user.id, request, uow)
    return order_resp


# ──────────────────────────────────────────────────────────────────────────────
# 3. Order Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/orders",
    response_model=list[OrderResponse],
    status_code=status.HTTP_200_OK,
    summary="List consumer orders",
)
def list_orders(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_sync_db),
) -> list[OrderResponse]:
    """List past and active orders placed by the authenticated consumer."""
    return CommerceService.list_consumer_orders(current_user.id, session)


@router.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Get order details",
)
def get_order(
    order_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_sync_db),
) -> OrderResponse:
    """Retrieve full order details including line items, store info, and compliance audit trail."""
    return CommerceService.get_order(order_id, current_user.id, session)
