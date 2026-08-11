"""
Cart management & checkout pipeline integration.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from faccp_common.exceptions import NotFoundError, ValidationError
from faccp_common.logging import get_logger
from app.config import get_settings
from app.db.models import Cart, CartItem

logger = get_logger(__name__)
settings = get_settings()


class CartService:

    def __init__(self, db: AsyncSession, http_client: httpx.AsyncClient | None = None) -> None:
        self.db = db
        self._http = http_client or httpx.AsyncClient(timeout=10.0)

    async def get_or_create_cart(self, consumer_id: str, store_id: str, jurisdiction_code: str = "IN-KA") -> Cart:
        result = await self.db.execute(
            select(Cart)
            .options(selectinload(Cart.items))
            .where(Cart.consumer_id == consumer_id, Cart.store_id == store_id)
        )
        cart = result.scalar_one_or_none()
        if cart is None:
            cart = Cart(
                id=str(uuid.uuid4()),
                consumer_id=consumer_id,
                store_id=store_id,
                jurisdiction_code=jurisdiction_code,
                expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            )
            self.db.add(cart)
            await self.db.commit()
            await self.db.refresh(cart, attribute_names=["items"])
        return cart

    async def add_item(self, consumer_id: str, store_id: str, product_id: str, sku: str, quantity: int = 1) -> Cart:
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero")
        cart = await self.get_or_create_cart(consumer_id, store_id)
        for item in cart.items:
            if item.product_id == product_id and item.sku == sku:
                item.quantity += quantity
                await self.db.commit()
                return cart

        new_item = CartItem(
            id=str(uuid.uuid4()),
            cart_id=cart.id,
            product_id=product_id,
            sku=sku,
            quantity=quantity,
            unit_price=Decimal("100.00"),
        )
        self.db.add(new_item)
        await self.db.commit()
        await self.db.refresh(cart, attribute_names=["items"])
        return cart

    async def remove_item(self, consumer_id: str, store_id: str, item_id: str) -> Cart:
        cart = await self.get_or_create_cart(consumer_id, store_id)
        for item in cart.items:
            if item.id == item_id:
                await self.db.delete(item)
                await self.db.commit()
                break
        await self.db.refresh(cart, attribute_names=["items"])
        return cart

    async def apply_promotion(self, consumer_id: str, store_id: str, promo_code: str) -> Cart:
        cart = await self.get_or_create_cart(consumer_id, store_id)
        cart.applied_promotion_code = promo_code
        await self.db.commit()
        return cart

    async def calculate_totals(self, cart: Cart) -> dict[str, Any]:
        payload = {
            "store_id": cart.store_id,
            "jurisdiction_code": cart.jurisdiction_code,
            "currency": "INR",
            "promotion_code": cart.applied_promotion_code,
            "items": [
                {
                    "product_id": item.product_id,
                    "sku": item.sku,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price),
                }
                for item in cart.items
            ],
        }
        try:
            resp = await self._http.post(f"{settings.pricing_service_url}/api/v1/pricing/calculate", json=payload)
            if resp.status_code == 200:
                return resp.json()["data"]
        except Exception:
            logger.exception("pricing_service_call_failed", cart_id=cart.id)

        # Fallback local calculation
        subtotal = sum(item.unit_price * item.quantity for item in cart.items)
        return {
            "subtotal": float(subtotal),
            "discount_amount": 0.0,
            "tax_amount": float(subtotal * Decimal("0.18")),
            "delivery_fee": 50.0,
            "platform_fee": 15.0,
            "total_amount": float(subtotal * Decimal("1.18") + Decimal("65")),
            "currency": "INR",
            "applied_promotion": cart.applied_promotion_code,
            "snapshot_id": f"snap_{uuid.uuid4().hex[:12]}",
        }
