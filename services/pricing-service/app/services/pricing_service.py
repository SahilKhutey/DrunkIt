"""
Pricing service — product pricing, promotions, tax calculation.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.exceptions import NotFoundError, ValidationError
from faccp_common.kafka_client import EventProducer
from faccp_common.logging import get_logger
from app.config import get_settings
from app.db.models import (
    PriceBook, PriceBookEntry, Promotion,
    PriceCalculation, TaxRule,
)
from app.schemas.pricing import (
    CalculateRequest, CalculateResponse, CreatePriceBookRequest,
    CreatePromotionRequest, PriceLineItem,
)

logger = get_logger(__name__)
settings = get_settings()


class PricingService:

    def __init__(self, db: AsyncSession, producer: EventProducer | None = None) -> None:
        self.db = db
        self.producer = producer

    async def create_price_book(self, payload: CreatePriceBookRequest) -> PriceBook:
        pb = PriceBook(
            id=str(uuid.uuid4()), name=payload.name,
            store_id=payload.store_id, retailer_id=payload.retailer_id,
            effective_from=payload.effective_from,
            effective_until=payload.effective_until, is_active=True,
        )
        self.db.add(pb)
        for entry in payload.entries:
            self.db.add(PriceBookEntry(
                id=str(uuid.uuid4()), price_book_id=pb.id,
                product_id=entry.product_id, sku=entry.sku,
                base_price=entry.base_price, min_quantity=entry.min_quantity,
                max_quantity=entry.max_quantity,
            ))
        await self.db.commit()
        return pb

    async def create_promotion(self, payload: CreatePromotionRequest) -> Promotion:
        if payload.discount_type == "percentage" and (payload.discount_value <= 0 or payload.discount_value > 100):
            raise ValidationError("Percentage discount must be between 0 and 100")
        promo = Promotion(
            id=str(uuid.uuid4()), code=payload.code, name=payload.name,
            description=payload.description, discount_type=payload.discount_type,
            discount_value=payload.discount_value, min_order_amount=payload.min_order_amount,
            max_discount_amount=payload.max_discount_amount,
            applicable_categories=payload.applicable_categories,
            applicable_products=payload.applicable_products,
            valid_from=payload.valid_from, valid_until=payload.valid_until,
            max_total_uses=payload.max_total_uses, max_uses_per_user=payload.max_uses_per_user,
            is_active=True,
        )
        self.db.add(promo)
        await self.db.commit()
        return promo

    async def calculate(
        self, payload: CalculateRequest, consumer_id: str | None = None
    ) -> CalculateResponse:
        now = datetime.now(timezone.utc)
        line_items: list[dict[str, Any]] = []
        subtotal = Decimal("0")

        for item in payload.items:
            price = await self._get_price(
                payload.store_id, item.product_id, item.sku, item.quantity, now
            )
            line_total = price * item.quantity
            subtotal += line_total
            line_items.append({
                "product_id": item.product_id, "sku": item.sku,
                "quantity": item.quantity, "unit_price": float(price),
                "line_total": float(line_total), "applied_rule": None,
            })

        discount_amount = Decimal("0")
        applied_promotion = None
        if payload.promotion_code:
            promo = await self._get_active_promotion(payload.promotion_code, now)
            if promo:
                if subtotal >= promo.min_order_amount:
                    if promo.discount_type == "percentage":
                        discount_amount = subtotal * Decimal(str(promo.discount_value)) / Decimal("100")
                    elif promo.discount_type == "fixed":
                        discount_amount = Decimal(str(promo.discount_value))
                    if promo.max_discount_amount:
                        discount_amount = min(discount_amount, Decimal(str(promo.max_discount_amount)))
                    applied_promotion = promo.code

        tax_amount = await self._calculate_tax(subtotal - discount_amount, payload.jurisdiction_code, payload.items)
        delivery_fee = payload.delivery_fee
        platform_fee = self._calculate_platform_fee(subtotal)
        total = subtotal - discount_amount + tax_amount + delivery_fee + platform_fee

        snapshot = PriceCalculation(
            id=str(uuid.uuid4()), consumer_id=consumer_id, store_id=payload.store_id,
            subtotal=subtotal, discount_amount=discount_amount, tax_amount=tax_amount,
            delivery_fee=delivery_fee, platform_fee=platform_fee, total_amount=total,
            currency=payload.currency, applied_promotion_code=applied_promotion,
            line_items=line_items, calculated_at=now,
        )
        self.db.add(snapshot)
        await self.db.commit()

        return CalculateResponse(
            subtotal=subtotal, discount_amount=discount_amount, tax_amount=tax_amount,
            delivery_fee=delivery_fee, platform_fee=platform_fee, total_amount=total,
            currency=payload.currency, applied_promotion=applied_promotion,
            line_items=line_items, snapshot_id=snapshot.id, calculated_at=now,
        )

    async def _get_price(
        self, store_id: str, product_id: str, sku: str, quantity: int, at: datetime
    ) -> Decimal:
        result = await self.db.execute(
            select(PriceBook).where(
                PriceBook.store_id == store_id, PriceBook.is_active == True,
            ).order_by(PriceBook.created_at.desc())
        )
        pb = result.scalars().first()
        if pb is None:
            return Decimal("100.00")  # Fallback default price for testing

        result = await self.db.execute(
            select(PriceBookEntry).where(
                PriceBookEntry.price_book_id == pb.id,
                PriceBookEntry.product_id == product_id,
            )
        )
        entry = result.scalars().first()
        if entry is None:
            return Decimal("100.00")
        return Decimal(str(entry.base_price))

    async def _get_active_promotion(self, code: str, at: datetime) -> Promotion | None:
        result = await self.db.execute(
            select(Promotion).where(
                Promotion.code == code, Promotion.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    async def _calculate_tax(
        self, taxable_amount: Decimal, jurisdiction_code: str, items: list[PriceLineItem]
    ) -> Decimal:
        result = await self.db.execute(
            select(TaxRule).where(
                TaxRule.jurisdiction_code == jurisdiction_code,
                TaxRule.is_active == True,
            )
        )
        rules = {r.category: r for r in result.scalars().all()}
        total_tax = Decimal("0")
        for item in items:
            rate = Decimal("0.18")
            if item.category and item.category in rules:
                rate = Decimal(str(rules[item.category].rate))
            line_price = Decimal(str(item.unit_price)) if item.unit_price else Decimal("100.00")
            line_tax = line_price * item.quantity * rate
            total_tax += line_tax
        return total_tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _calculate_platform_fee(self, subtotal: Decimal) -> Decimal:
        return (subtotal * Decimal(str(settings.platform_commission_pct)) / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
