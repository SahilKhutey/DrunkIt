"""Commerce domain service managing Shopping Carts, Compliance-Gated Checkout, and Order Lifecycle."""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import (
    ComplianceDeniedError,
    ConflictError,
    ResourceNotFoundError,
    ValidationError,
)
from app.db.uow import SyncUnitOfWork
from app.models.catalog import Product, ProductVariant, SKU
from app.models.commerce import Cart, CartItem, Order, OrderItem
from app.models.inventory import Price, RetailerSKU
from app.models.retailer import Jurisdiction, Retailer, RetailerLocation
from app.schemas.commerce import (
    CartItemAdd,
    CartItemResponse,
    CartResponse,
    CheckoutRequest,
    OrderItemResponse,
    OrderResponse,
)
from app.schemas.compliance import ComplianceCheckRequest
from app.services.compliance_service import ComplianceService


def _format_inr(amount_minor: int) -> str:
    """Format minor currency units (paise) into INR string."""
    rupees = amount_minor / 100.0
    return f"₹{rupees:,.2f}"


class CommerceService:
    """Service handling active shopping cart items, compliance gates, and orders."""

    # 1. Cart Management
    @staticmethod
    def get_or_create_cart(consumer_id: uuid.UUID, session: Session) -> Cart:
        """Fetch active shopping cart or create a new one."""
        cart = session.scalars(
            select(Cart).where(Cart.consumer_id == consumer_id, Cart.status == "ACTIVE")
        ).first()

        if not cart:
            cart = Cart(consumer_id=consumer_id, status="ACTIVE")
            session.add(cart)
            session.flush()

        return cart

    @classmethod
    def add_item_to_cart(
        cls,
        consumer_id: uuid.UUID,
        data: CartItemAdd,
        uow: SyncUnitOfWork,
    ) -> CartResponse:
        """Add or update an item in the active cart with active price snapshot."""
        session = uow.session
        cart = cls.get_or_create_cart(consumer_id, session)

        sku = session.get(SKU, data.sku_id)
        if not sku:
            raise ResourceNotFoundError(f"SKU '{data.sku_id}' was not found.")

        location = session.get(RetailerLocation, data.retailer_location_id)
        if not location:
            raise ResourceNotFoundError(f"Retailer location '{data.retailer_location_id}' was not found.")

        # Find RetailerSKU and active Price
        ret_sku = session.scalars(
            select(RetailerSKU)
            .where(
                RetailerSKU.retailer_location_id == data.retailer_location_id,
                RetailerSKU.sku_id == data.sku_id,
            )
            .options(selectinload(RetailerSKU.prices))
        ).first()

        now = datetime.now(timezone.utc)
        unit_price_minor = 250000  # Default fallback ₹2,500.00
        if ret_sku and ret_sku.prices:
            for p in ret_sku.prices:
                p_from = p.effective_from if p.effective_from.tzinfo else p.effective_from.replace(tzinfo=timezone.utc)
                p_to = p.effective_to
                if p_to and not p_to.tzinfo:
                    p_to = p_to.replace(tzinfo=timezone.utc)
                if p_from <= now and (p_to is None or p_to >= now):
                    unit_price_minor = p.amount_minor
                    break

        # Check existing item in cart
        existing_item = session.scalars(
            select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.sku_id == data.sku_id,
                CartItem.retailer_location_id == data.retailer_location_id,
            )
        ).first()

        if existing_item:
            existing_item.quantity += data.quantity
            existing_item.price_snapshot = {"amount_minor": unit_price_minor, "currency": "INR"}
        else:
            new_item = CartItem(
                cart_id=cart.id,
                sku_id=data.sku_id,
                retailer_location_id=data.retailer_location_id,
                quantity=data.quantity,
                price_snapshot={"amount_minor": unit_price_minor, "currency": "INR"},
            )
            session.add(new_item)

        # Set Cart jurisdiction to match store location state
        jur = session.scalars(
            select(Jurisdiction).where(
                Jurisdiction.country_code == "IN",
                Jurisdiction.state_code == location.state_code,
            )
        ).first()
        if jur:
            cart.jurisdiction_id = jur.id

        session.flush()

        uow.publish_outbox(
            event_type="CART_UPDATED",
            aggregate_type="Cart",
            aggregate_id=cart.id,
            payload={"consumer_id": str(consumer_id), "sku_id": str(data.sku_id)},
        )

        return cls.format_cart_response(cart, session)

    @classmethod
    def remove_item_from_cart(
        cls,
        consumer_id: uuid.UUID,
        item_id: uuid.UUID,
        uow: SyncUnitOfWork,
    ) -> CartResponse:
        """Remove a line item from the shopping cart."""
        session = uow.session
        cart = cls.get_or_create_cart(consumer_id, session)

        item = session.scalars(
            select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id)
        ).first()
        if not item:
            raise ResourceNotFoundError(f"Cart item '{item_id}' was not found in active cart.")

        session.delete(item)
        session.flush()

        return cls.format_cart_response(cart, session)

    @classmethod
    def format_cart_response(cls, cart: Cart, session: Session) -> CartResponse:
        """Format Cart model and items into rich CartResponse schema."""
        items = list(
            session.scalars(
                select(CartItem)
                .where(CartItem.cart_id == cart.id)
                .options(
                    selectinload(CartItem.sku)
                    .selectinload(SKU.variant)
                    .selectinload(ProductVariant.product),
                    selectinload(CartItem.location)
                    .selectinload(RetailerLocation.retailer),
                )
            ).all()
        )

        item_responses: list[CartItemResponse] = []
        subtotal_minor = 0
        total_volume_ml = 0

        for item in items:
            unit_price = item.price_snapshot.get("amount_minor", 0) if item.price_snapshot else 0
            item_total = unit_price * item.quantity
            subtotal_minor += item_total

            vol = item.sku.variant.volume_ml if item.sku and item.sku.variant else 750
            total_volume_ml += vol * item.quantity

            item_responses.append(
                CartItemResponse(
                    id=item.id,
                    sku_id=item.sku_id,
                    canonical_code=item.sku.canonical_code if item.sku else "",
                    product_name=item.sku.variant.product.name if item.sku and item.sku.variant and item.sku.variant.product else "Spirit",
                    volume_ml=vol,
                    retailer_location_id=item.retailer_location_id,
                    retailer_name=item.location.retailer.display_name if item.location and item.location.retailer else "Licensed Retailer",
                    quantity=item.quantity,
                    unit_price_minor=unit_price,
                    unit_price_formatted=_format_inr(unit_price),
                    total_price_minor=item_total,
                    total_price_formatted=_format_inr(item_total),
                )
            )

        return CartResponse(
            id=cart.id,
            consumer_id=cart.consumer_id,
            jurisdiction_id=cart.jurisdiction_id,
            items=item_responses,
            item_count=len(item_responses),
            subtotal_minor=subtotal_minor,
            subtotal_formatted=_format_inr(subtotal_minor),
            total_volume_ml=total_volume_ml,
            status=cart.status,
        )

    # 2. Compliance-Gated Checkout & Order Lifecycle
    @classmethod
    def checkout_cart(
        cls,
        consumer_id: uuid.UUID,
        request: CheckoutRequest,
        uow: SyncUnitOfWork,
    ) -> OrderResponse:
        """Execute atomic compliance-gated checkout on the consumer's active cart."""
        session = uow.session

        # 1. Idempotency Check: Prevent duplicate order processing
        existing_order = session.scalars(
            select(Order)
            .where(
                Order.consumer_id == consumer_id,
                Order.idempotency_key == request.idempotency_key,
            )
            .options(
                selectinload(Order.items)
                .selectinload(OrderItem.sku)
                .selectinload(SKU.variant)
                .selectinload(ProductVariant.product),
                selectinload(Order.location).selectinload(RetailerLocation.retailer),
            )
        ).first()

        if existing_order:
            return cls.format_order_response(existing_order, session)

        # 2. Retrieve Active Cart
        cart = cls.get_or_create_cart(consumer_id, session)
        items = list(
            session.scalars(
                select(CartItem)
                .where(CartItem.cart_id == cart.id)
                .options(
                    selectinload(CartItem.sku)
                    .selectinload(SKU.variant)
                    .selectinload(ProductVariant.product),
                    selectinload(CartItem.location)
                    .selectinload(RetailerLocation.retailer),
                )
            ).all()
        )
        if not items:
            raise ValidationError("Shopping cart is empty. Add items before checking out.")

        # Fulfilling store location from first item
        first_item = items[0]
        location = session.get(RetailerLocation, first_item.retailer_location_id)
        if not location:
            raise ResourceNotFoundError(f"Store location '{first_item.retailer_location_id}' was not found.")

        # Calculate totals
        subtotal_minor = 0
        total_volume_ml = 0
        product_class = "SPIRITS"

        for item in items:
            unit_price = item.price_snapshot.get("amount_minor", 0) if item.price_snapshot else 0
            subtotal_minor += unit_price * item.quantity
            vol = item.sku.variant.volume_ml if item.sku and item.sku.variant else 750
            total_volume_ml += vol * item.quantity
            if item.sku and item.sku.variant and item.sku.variant.product:
                product_class = item.sku.variant.product.product_type

        # 3. Deterministic Compliance Check Execution
        correlation_id = uuid.uuid4()
        check_now = request.current_time or datetime.now(timezone.utc)
        compliance_req = ComplianceCheckRequest(
            correlation_id=correlation_id,
            jurisdiction_code=f"IN-{location.state_code}",
            consumer_id=consumer_id,
            consumer_age=request.consumer_age,
            is_age_verified=request.is_age_verified,
            retailer_id=location.retailer_id,
            retailer_location_id=location.id,
            product_class=product_class,
            channel=request.channel,
            quantity=len(items),
            total_volume_ml=total_volume_ml,
            current_time=check_now,
        )

        compliance_decision = ComplianceService.evaluate_compliance(compliance_req, uow)

        if compliance_decision.decision != "ALLOWED":
            reasons_str = ", ".join(compliance_decision.reason_codes)
            raise ComplianceDeniedError(
                message=f"Order checkout rejected by compliance engine: {reasons_str}",
                details={
                    "decision": compliance_decision.decision,
                    "reasons": compliance_decision.reason_codes,
                    "required_checks": compliance_decision.required_checks,
                    "jurisdiction": compliance_decision.jurisdiction_code,
                },
            )

        # 4. Create Order Record
        order = Order(
            consumer_id=consumer_id,
            retailer_location_id=location.id,
            status="CONFIRMED",
            currency="INR",
            subtotal_minor=subtotal_minor,
            total_minor=subtotal_minor,
            compliance_decision_id=compliance_decision.check_id,
            idempotency_key=request.idempotency_key,
        )
        session.add(order)
        session.flush()

        # 5. Create Order Items
        for item in items:
            unit_price = item.price_snapshot.get("amount_minor", 0) if item.price_snapshot else 0
            order_item = OrderItem(
                order_id=order.id,
                sku_id=item.sku_id,
                quantity=item.quantity,
                unit_price_minor=unit_price,
            )
            session.add(order_item)

        # 6. Clear active cart items
        for item in items:
            session.delete(item)
        session.flush()

        # 7. Audit & Outbox Dispatch
        uow.record_audit(
            actor_id=consumer_id,
            action="ORDER_CREATED",
            entity_type="Order",
            entity_id=order.id,
            correlation_id=correlation_id,
            metadata={
                "order_id": str(order.id),
                "total_minor": order.total_minor,
                "location_id": str(location.id),
                "compliance_check_id": str(compliance_decision.check_id),
            },
        )
        uow.publish_outbox(
            event_type="ORDER_CREATED",
            aggregate_type="Order",
            aggregate_id=order.id,
            correlation_id=correlation_id,
            payload={
                "order_id": str(order.id),
                "consumer_id": str(consumer_id),
                "total_minor": order.total_minor,
                "compliance_decision_id": str(compliance_decision.check_id),
            },
        )

        return cls.format_order_response(order, session)

    @classmethod
    def get_order(
        cls,
        order_id: uuid.UUID,
        consumer_id: uuid.UUID,
        session: Session,
    ) -> OrderResponse:
        """Fetch specific order details for an authenticated consumer."""
        order = session.scalars(
            select(Order)
            .where(Order.id == order_id, Order.consumer_id == consumer_id)
            .options(
                selectinload(Order.items)
                .selectinload(OrderItem.sku)
                .selectinload(SKU.variant)
                .selectinload(ProductVariant.product),
                selectinload(Order.location).selectinload(RetailerLocation.retailer),
            )
        ).first()

        if not order:
            raise ResourceNotFoundError(f"Order '{order_id}' was not found.")

        return cls.format_order_response(order, session)

    @classmethod
    def list_consumer_orders(
        cls,
        consumer_id: uuid.UUID,
        session: Session,
    ) -> list[OrderResponse]:
        """List past and active orders for a consumer."""
        orders = session.scalars(
            select(Order)
            .where(Order.consumer_id == consumer_id)
            .order_by(Order.created_at.desc())
            .options(
                selectinload(Order.items)
                .selectinload(OrderItem.sku)
                .selectinload(SKU.variant)
                .selectinload(ProductVariant.product),
                selectinload(Order.location).selectinload(RetailerLocation.retailer),
            )
        ).all()

        return [cls.format_order_response(o, session) for o in orders]

    @classmethod
    def format_order_response(cls, order: Order, session: Session) -> OrderResponse:
        """Format Order model and line items into OrderResponse schema."""
        items = list(
            session.scalars(
                select(OrderItem)
                .where(OrderItem.order_id == order.id)
                .options(
                    selectinload(OrderItem.sku)
                    .selectinload(SKU.variant)
                    .selectinload(ProductVariant.product),
                )
            ).all()
        )

        location = session.get(RetailerLocation, order.retailer_location_id)
        retailer_name = "Licensed Retailer"
        if location and location.retailer:
            retailer_name = location.retailer.display_name

        items_resp: list[OrderItemResponse] = []
        for itm in items:
            vol = itm.sku.variant.volume_ml if itm.sku and itm.sku.variant else 750
            total_price = itm.unit_price_minor * itm.quantity
            items_resp.append(
                OrderItemResponse(
                    id=itm.id,
                    sku_id=itm.sku_id,
                    canonical_code=itm.sku.canonical_code if itm.sku else "",
                    product_name=itm.sku.variant.product.name if itm.sku and itm.sku.variant and itm.sku.variant.product else "Spirit",
                    volume_ml=vol,
                    quantity=itm.quantity,
                    unit_price_minor=itm.unit_price_minor,
                    unit_price_formatted=_format_inr(itm.unit_price_minor),
                    total_price_minor=total_price,
                    total_price_formatted=_format_inr(total_price),
                )
            )

        return OrderResponse(
            id=order.id,
            consumer_id=order.consumer_id,
            retailer_location_id=order.retailer_location_id,
            retailer_name=retailer_name,
            status=order.status,
            currency=order.currency,
            subtotal_minor=order.subtotal_minor,
            total_minor=order.total_minor,
            total_formatted=_format_inr(order.total_minor),
            compliance_decision_id=order.compliance_decision_id,
            idempotency_key=order.idempotency_key,
            items=items_resp,
            created_at=order.created_at,
        )
