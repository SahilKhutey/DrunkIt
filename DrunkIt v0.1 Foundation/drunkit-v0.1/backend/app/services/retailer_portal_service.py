"""Retailer portal service for bulk POS inventory feeds, store fulfillment queues, and analytics."""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import (
    ConflictError,
    ResourceNotFoundError,
    ValidationError,
)
from app.db.uow import SyncUnitOfWork
from app.models.commerce import Order, OrderItem
from app.models.inventory import InventorySnapshot, Price, RetailerSKU
from app.models.retailer import RetailerLocation
from app.schemas.commerce import OrderResponse
from app.schemas.retailer_portal import (
    BulkInventoryFeedRequest,
    BulkInventoryFeedResponse,
    RetailerStoreDashboardResponse,
    RetailerStoreOrdersResponse,
)
from app.services.commerce_service import CommerceService

# Allowed order state machine transitions
ALLOWED_TRANSITIONS: dict[str, list[str]] = {
    "PENDING": ["CONFIRMED", "CANCELLED"],
    "CONFIRMED": ["PREPARING", "CANCELLED"],
    "PREPARING": ["READY_FOR_PICKUP", "CANCELLED"],
    "READY_FOR_PICKUP": ["OUT_FOR_DELIVERY", "FULFILLED", "CANCELLED"],
    "OUT_FOR_DELIVERY": ["FULFILLED", "CANCELLED"],
    "FULFILLED": [],
    "CANCELLED": [],
}


def _format_inr(amount_minor: int) -> str:
    """Format minor currency units (paise) into INR string."""
    rupees = amount_minor / 100.0
    return f"₹{rupees:,.2f}"


class RetailerPortalService:
    """Service handling store-level operations, POS sync feeds, and order fulfillment."""

    # 1. Bulk POS Inventory Ingestion
    @classmethod
    def ingest_bulk_pos_feed(
        cls,
        location_id: uuid.UUID,
        request: BulkInventoryFeedRequest,
        uow: SyncUnitOfWork,
    ) -> BulkInventoryFeedResponse:
        """Process bulk POS inventory snapshots and statutory price updates for a store location."""
        session = uow.session
        location = session.get(RetailerLocation, location_id)
        if not location:
            raise ResourceNotFoundError(f"Store location '{location_id}' was not found.")

        # Load all mapped SKUs for this store
        mapped_skus_list = list(
            session.scalars(
                select(RetailerSKU).where(RetailerSKU.retailer_location_id == location_id)
            ).all()
        )
        mapped_by_external = {sku.external_sku: sku for sku in mapped_skus_list if sku.external_sku}

        now = datetime.now(timezone.utc)
        mapped_count = 0
        unmapped_count = 0
        unmapped_skus: list[str] = []
        snapshots_created = 0
        prices_updated = 0

        for item in request.items:
            ext_sku = item.external_sku.strip()
            ret_sku = mapped_by_external.get(ext_sku)

            if not ret_sku:
                unmapped_count += 1
                unmapped_skus.append(ext_sku)
                continue

            mapped_count += 1

            # Determine availability status
            if item.quantity <= 0:
                avail_status = "OUT_OF_STOCK"
            elif item.quantity <= 5:
                avail_status = "LOW_STOCK"
            else:
                avail_status = "IN_STOCK"

            # Create Inventory Snapshot
            snapshot = InventorySnapshot(
                retailer_sku_id=ret_sku.id,
                quantity=item.quantity,
                availability_status=avail_status,
                source=request.source,
                captured_at=now,
            )
            session.add(snapshot)
            snapshots_created += 1

            # Update Price if provided
            if item.price_minor is not None:
                price = Price(
                    retailer_sku_id=ret_sku.id,
                    amount_minor=item.price_minor,
                    currency="INR",
                    effective_from=now,
                    captured_at=now,
                )
                session.add(price)
                prices_updated += 1

        session.flush()

        # Audit Log & Outbox Event
        uow.publish_outbox(
            event_type="INVENTORY_FEED_SYNCED",
            aggregate_type="RetailerLocation",
            aggregate_id=location_id,
            payload={
                "location_id": str(location_id),
                "snapshots_created": snapshots_created,
                "prices_updated": prices_updated,
                "unmapped_count": unmapped_count,
            },
        )

        return BulkInventoryFeedResponse(
            total_items=len(request.items),
            mapped_count=mapped_count,
            unmapped_count=unmapped_count,
            unmapped_skus=unmapped_skus,
            snapshots_created=snapshots_created,
            prices_updated=prices_updated,
        )

    # 2. Store Order Fulfillment Queue
    @classmethod
    def list_store_orders(
        cls,
        location_id: uuid.UUID,
        session: Session,
        status_filter: str | None = None,
    ) -> RetailerStoreOrdersResponse:
        """List incoming orders for a store location."""
        location = session.get(RetailerLocation, location_id)
        if not location:
            raise ResourceNotFoundError(f"Store location '{location_id}' was not found.")

        stmt = (
            select(Order)
            .where(Order.retailer_location_id == location_id)
            .order_by(Order.created_at.desc())
        )
        if status_filter:
            stmt = stmt.where(Order.status == status_filter.upper())

        orders = list(session.scalars(stmt).all())
        order_responses = [CommerceService.format_order_response(o, session) for o in orders]

        pending_count = sum(
            1 for o in orders if o.status in ["CONFIRMED", "PREPARING", "READY_FOR_PICKUP"]
        )

        return RetailerStoreOrdersResponse(
            location_id=location.id,
            location_name=location.name,
            orders=order_responses,
            total_orders=len(orders),
            pending_fulfillment_count=pending_count,
        )

    @classmethod
    def update_store_order_status(
        cls,
        location_id: uuid.UUID,
        order_id: uuid.UUID,
        new_status: str,
        uow: SyncUnitOfWork,
        actor_id: uuid.UUID,
    ) -> OrderResponse:
        """Transition order lifecycle status with state-machine validation."""
        session = uow.session
        order = session.scalars(
            select(Order).where(
                Order.id == order_id,
                Order.retailer_location_id == location_id,
            )
        ).first()

        if not order:
            raise ResourceNotFoundError(f"Order '{order_id}' was not found at this store location.")

        target_status = new_status.strip().upper()
        allowed = ALLOWED_TRANSITIONS.get(order.status, [])

        if target_status not in allowed:
            raise ValidationError(
                f"Invalid order transition from '{order.status}' to '{target_status}'. Allowed: {allowed}"
            )

        old_status = order.status
        order.status = target_status
        session.flush()

        # Audit and Outbox
        uow.record_audit(
            actor_id=actor_id,
            action="ORDER_STATUS_CHANGED",
            entity_type="Order",
            entity_id=order.id,
            metadata={"old_status": old_status, "new_status": target_status},
        )
        uow.publish_outbox(
            event_type="ORDER_STATUS_CHANGED",
            aggregate_type="Order",
            aggregate_id=order.id,
            payload={
                "order_id": str(order.id),
                "old_status": old_status,
                "new_status": target_status,
            },
        )

        return CommerceService.format_order_response(order, session)

    # 3. Store Dashboard & Analytics
    @classmethod
    def get_store_dashboard(
        cls,
        location_id: uuid.UUID,
        session: Session,
    ) -> RetailerStoreDashboardResponse:
        """Compute live operational dashboard metrics for a store location."""
        location = session.get(RetailerLocation, location_id)
        if not location:
            raise ResourceNotFoundError(f"Store location '{location_id}' was not found.")

        mapped_skus = list(
            session.scalars(
                select(RetailerSKU)
                .where(RetailerSKU.retailer_location_id == location_id)
                .options(selectinload(RetailerSKU.snapshots))
            ).all()
        )

        in_stock = 0
        low_stock = 0
        out_of_stock = 0

        for r_sku in mapped_skus:
            latest_snap = None
            if r_sku.snapshots:
                latest_snap = max(
                    r_sku.snapshots,
                    key=lambda s: s.captured_at if s.captured_at.tzinfo else s.captured_at.replace(tzinfo=timezone.utc),
                )

            if not latest_snap or latest_snap.availability_status == "OUT_OF_STOCK":
                out_of_stock += 1
            elif latest_snap.availability_status == "LOW_STOCK":
                low_stock += 1
            else:
                in_stock += 1

        # Orders & GMV
        orders = list(
            session.scalars(
                select(Order).where(Order.retailer_location_id == location_id)
            ).all()
        )

        total_gmv = sum(o.total_minor for o in orders if o.status != "CANCELLED")

        return RetailerStoreDashboardResponse(
            location_id=location.id,
            location_name=location.name,
            active_skus_count=len(mapped_skus),
            in_stock_skus_count=in_stock,
            low_stock_skus_count=low_stock,
            out_of_stock_skus_count=out_of_stock,
            total_orders_count=len(orders),
            total_gmv_minor=total_gmv,
            total_gmv_formatted=_format_inr(total_gmv),
        )
