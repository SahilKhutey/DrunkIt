"""Retailer network, inventory ingestion, pricing, and live availability service."""

import math
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import ConflictError, ResourceNotFoundError, ValidationError
from app.db.uow import SyncUnitOfWork
from app.models.catalog import Product, ProductVariant, SKU
from app.models.inventory import InventorySnapshot, Price, RetailerSKU
from app.models.retailer import (
    Jurisdiction,
    Retailer,
    RetailerLicence,
    RetailerLocation,
)
from app.schemas.retailer import (
    InventorySnapshotCreate,
    PriceCreate,
    ProductAvailabilityResponse,
    RetailerCreate,
    RetailerLicenceCreate,
    RetailerLocationCreate,
    RetailerSKUMapRequest,
    StoreAvailabilityItem,
)


def _haversine_distance_km(
    lat1: float | Decimal, lon1: float | Decimal, lat2: float | Decimal, lon2: float | Decimal
) -> float:
    """Calculate the great-circle distance between two points on the Earth in kilometers."""
    r = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(float(lat2) - float(lat1))
    dlon = math.radians(float(lon2) - float(lon1))
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(float(lat1)))
        * math.cos(math.radians(float(lat2)))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(r * c, 2)


def _format_inr_price(amount_minor: int) -> str:
    """Format minor currency units (paise) into human-readable INR string."""
    rupees = amount_minor / 100.0
    return f"₹{rupees:,.2f}"


def _ensure_utc(dt: datetime | None) -> datetime | None:
    """Ensure datetime has UTC timezone."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class RetailerService:
    """Service managing retailer network, catalog mapping, and live inventory availability."""

    # 1. Retailer Lifecycle
    @classmethod
    def create_retailer(
        cls,
        data: RetailerCreate,
        uow: SyncUnitOfWork,
        actor_id: uuid.UUID | None = None,
    ) -> Retailer:
        """Onboard a new retailer organization."""
        session = uow.session
        retailer = Retailer(
            legal_name=data.legal_name,
            display_name=data.display_name,
            status="ACTIVE",
            licence_status="PENDING",
        )
        session.add(retailer)
        session.flush()

        uow.record_audit(
            actor_id=actor_id,
            action="RETAILER_CREATED",
            entity_type="Retailer",
            entity_id=retailer.id,
            metadata={"legal_name": retailer.legal_name, "display_name": retailer.display_name},
        )
        uow.publish_outbox(
            event_type="RETAILER_CREATED",
            aggregate_type="Retailer",
            aggregate_id=retailer.id,
            payload={"retailer_id": str(retailer.id), "display_name": retailer.display_name},
        )
        return retailer

    @staticmethod
    def get_retailer(retailer_id: uuid.UUID, session: Session) -> Retailer | None:
        """Fetch retailer with locations and licences."""
        return session.scalars(
            select(Retailer)
            .options(
                selectinload(Retailer.locations),
                selectinload(Retailer.licences),
            )
            .where(Retailer.id == retailer_id)
        ).first()

    @staticmethod
    def list_retailers(limit: int = 50, offset: int = 0, session: Session = None) -> list[Retailer]:  # type: ignore[assignment]
        """List active retailers."""
        return list(
            session.scalars(
                select(Retailer)
                .order_by(Retailer.display_name.asc())
                .offset(offset)
                .limit(limit)
            ).all()
        )

    # 2. Location & Licence
    @staticmethod
    def create_location(
        retailer_id: uuid.UUID,
        data: RetailerLocationCreate,
        session: Session,
    ) -> RetailerLocation:
        """Register a physical store location for a retailer."""
        retailer = session.get(Retailer, retailer_id)
        if not retailer:
            raise ResourceNotFoundError(f"Retailer '{retailer_id}' was not found.")

        location = RetailerLocation(
            retailer_id=retailer_id,
            name=data.name,
            address=data.address,
            city=data.city,
            state_code=data.state_code.upper(),
            postal_code=data.postal_code,
            country_code=data.country_code.upper(),
            latitude=data.latitude,
            longitude=data.longitude,
            status="ACTIVE",
        )
        session.add(location)
        session.flush()
        return location

    @staticmethod
    def create_licence(
        retailer_id: uuid.UUID,
        data: RetailerLicenceCreate,
        session: Session,
    ) -> RetailerLicence:
        """Register an excise licence for a retailer and mark licence status as VERIFIED."""
        retailer = session.get(Retailer, retailer_id)
        if not retailer:
            raise ResourceNotFoundError(f"Retailer '{retailer_id}' was not found.")

        jurisdiction = session.get(Jurisdiction, data.jurisdiction_id)
        if not jurisdiction:
            raise ResourceNotFoundError(f"Jurisdiction '{data.jurisdiction_id}' was not found.")

        licence = RetailerLicence(
            retailer_id=retailer_id,
            jurisdiction_id=data.jurisdiction_id,
            licence_number=data.licence_number,
            licence_type=data.licence_type,
            valid_from=data.valid_from,
            valid_to=data.valid_to,
            status="ACTIVE",
            evidence_uri=data.evidence_uri,
        )
        session.add(licence)
        retailer.licence_status = "VERIFIED"
        session.flush()
        return licence

    # 3. SKU Mapping, Inventory & Pricing
    @classmethod
    def map_sku(
        cls,
        location_id: uuid.UUID,
        data: RetailerSKUMapRequest,
        uow: SyncUnitOfWork,
    ) -> RetailerSKU:
        """Map a store location's internal POS SKU to a canonical SKU."""
        session = uow.session
        location = session.get(RetailerLocation, location_id)
        if not location:
            raise ResourceNotFoundError(f"Retailer location '{location_id}' was not found.")

        canonical_sku = session.get(SKU, data.sku_id)
        if not canonical_sku:
            raise ResourceNotFoundError(f"Canonical SKU '{data.sku_id}' was not found.")

        existing = session.scalars(
            select(RetailerSKU).where(
                RetailerSKU.retailer_location_id == location_id,
                RetailerSKU.sku_id == data.sku_id,
            )
        ).first()
        if existing:
            return existing

        ret_sku = RetailerSKU(
            retailer_location_id=location_id,
            sku_id=data.sku_id,
            external_sku=data.external_sku,
            external_name=data.external_name,
            status="ACTIVE",
        )
        session.add(ret_sku)
        session.flush()

        uow.publish_outbox(
            event_type="RETAILER_SKU_MAPPED",
            aggregate_type="RetailerSKU",
            aggregate_id=ret_sku.id,
            payload={
                "retailer_sku_id": str(ret_sku.id),
                "location_id": str(location_id),
                "sku_id": str(data.sku_id),
            },
        )
        return ret_sku

    @classmethod
    def ingest_inventory_snapshot(
        cls,
        data: InventorySnapshotCreate,
        uow: SyncUnitOfWork,
    ) -> InventorySnapshot:
        """Ingest a live inventory snapshot from POS or manual feed."""
        session = uow.session
        ret_sku = session.get(RetailerSKU, data.retailer_sku_id)
        if not ret_sku:
            raise ResourceNotFoundError(f"RetailerSKU '{data.retailer_sku_id}' was not found.")

        snapshot = InventorySnapshot(
            retailer_sku_id=data.retailer_sku_id,
            quantity=data.quantity,
            availability_status=data.availability_status,
            source=data.source,
            source_reference=data.source_reference,
            captured_at=datetime.now(timezone.utc),
        )
        session.add(snapshot)
        session.flush()

        uow.publish_outbox(
            event_type="INVENTORY_SNAPSHOT_INGESTED",
            aggregate_type="RetailerSKU",
            aggregate_id=ret_sku.id,
            payload={
                "retailer_sku_id": str(data.retailer_sku_id),
                "quantity": data.quantity,
                "status": data.availability_status,
            },
        )
        return snapshot

    @classmethod
    def set_price(
        cls,
        data: PriceCreate,
        uow: SyncUnitOfWork,
    ) -> Price:
        """Set or update the active price for a retailer SKU."""
        session = uow.session
        ret_sku = session.get(RetailerSKU, data.retailer_sku_id)
        if not ret_sku:
            raise ResourceNotFoundError(f"RetailerSKU '{data.retailer_sku_id}' was not found.")

        now = datetime.now(timezone.utc)
        price = Price(
            retailer_sku_id=data.retailer_sku_id,
            amount_minor=data.amount_minor,
            currency=data.currency,
            effective_from=data.effective_from or now,
            effective_to=data.effective_to,
            captured_at=now,
        )
        session.add(price)
        session.flush()

        uow.publish_outbox(
            event_type="PRICE_UPDATED",
            aggregate_type="RetailerSKU",
            aggregate_id=ret_sku.id,
            payload={
                "retailer_sku_id": str(data.retailer_sku_id),
                "amount_minor": data.amount_minor,
                "currency": data.currency,
            },
        )
        return price

    # 4. Live Availability Engine
    @staticmethod
    def get_product_availability(
        product_identifier: str | uuid.UUID,
        latitude: float | None = None,
        longitude: float | None = None,
        state_code: str | None = None,
        city: str | None = None,
        session: Session = None,  # type: ignore[assignment]
    ) -> ProductAvailabilityResponse:
        """Calculate real-time localized availability, stock quantity, and pricing across stores."""
        # 1. Resolve Product
        if isinstance(product_identifier, uuid.UUID):
            product = session.get(Product, product_identifier)
        else:
            try:
                p_uuid = uuid.UUID(product_identifier)
                product = session.get(Product, p_uuid)
            except ValueError:
                product = session.scalars(select(Product).where(Product.slug == product_identifier)).first()

        if not product:
            raise ResourceNotFoundError(f"Product '{product_identifier}' was not found.")

        # 2. Get all SKUs belonging to this product
        sku_records = session.scalars(
            select(SKU)
            .join(ProductVariant, SKU.variant_id == ProductVariant.id)
            .where(ProductVariant.product_id == product.id)
            .options(selectinload(SKU.variant))
        ).all()

        sku_ids = [s.id for s in sku_records]
        sku_map = {s.id: s for s in sku_records}

        if not sku_ids:
            return ProductAvailabilityResponse(
                product_id=product.id,
                product_name=product.name,
                product_slug=product.slug,
                stores_count=0,
                stores=[],
            )

        # 3. Find Retailer SKUs for these SKUs
        query = (
            select(RetailerSKU)
            .join(RetailerLocation, RetailerSKU.retailer_location_id == RetailerLocation.id)
            .join(Retailer, RetailerLocation.retailer_id == Retailer.id)
            .where(
                RetailerSKU.sku_id.in_(sku_ids),
                RetailerLocation.status == "ACTIVE",
                Retailer.status == "ACTIVE",
            )
            .options(
                selectinload(RetailerSKU.location).selectinload(RetailerLocation.retailer),
                selectinload(RetailerSKU.snapshots),
                selectinload(RetailerSKU.prices),
            )
        )

        if state_code:
            query = query.where(RetailerLocation.state_code == state_code.strip().upper())
        if city:
            query = query.where(func.lower(RetailerLocation.city) == city.strip().lower())

        ret_skus = session.scalars(query).all()

        store_items: list[StoreAvailabilityItem] = []
        now = datetime.now(timezone.utc)

        for rs in ret_skus:
            loc = rs.location
            ret = loc.retailer
            sku = sku_map.get(rs.sku_id)
            if not sku or not sku.variant:
                continue

            # Latest Inventory Snapshot
            latest_snap = None
            if rs.snapshots:
                latest_snap = max(rs.snapshots, key=lambda s: _ensure_utc(s.captured_at) or now)

            # Active Price
            active_price = None
            for p in rs.prices:
                eff_from = _ensure_utc(p.effective_from)
                eff_to = _ensure_utc(p.effective_to)
                if eff_from and eff_from <= now:
                    if eff_to is None or eff_to >= now:
                        active_price = p
                        break

            # If no price configured, fallback to 0 or skip
            price_minor = active_price.amount_minor if active_price else 0
            price_formatted = _format_inr_price(price_minor)
            availability_status = latest_snap.availability_status if latest_snap else "OUT_OF_STOCK"
            quantity = latest_snap.quantity if latest_snap else 0

            # Compute Distance if coordinates available
            distance_km: float | None = None
            if latitude is not None and longitude is not None and loc.latitude and loc.longitude:
                distance_km = _haversine_distance_km(latitude, longitude, loc.latitude, loc.longitude)

            item = StoreAvailabilityItem(
                retailer_id=ret.id,
                retailer_name=ret.display_name,
                location_id=loc.id,
                location_name=loc.name,
                address=loc.address,
                city=loc.city,
                state_code=loc.state_code,
                latitude=loc.latitude,
                longitude=loc.longitude,
                distance_km=distance_km,
                sku_id=sku.id,
                canonical_code=sku.canonical_code,
                volume_ml=sku.variant.volume_ml,
                availability_status=availability_status,
                quantity=quantity,
                price_minor=price_minor,
                price_formatted=price_formatted,
                currency="INR",
            )
            store_items.append(item)

        # Sort: in-stock first, then by distance if provided
        if latitude is not None and longitude is not None:
            store_items.sort(
                key=lambda x: (
                    0 if x.availability_status == "IN_STOCK" else 1,
                    x.distance_km if x.distance_km is not None else 999999,
                )
            )
        else:
            store_items.sort(
                key=lambda x: (
                    0 if x.availability_status == "IN_STOCK" else 1,
                    x.price_minor,
                )
            )

        return ProductAvailabilityResponse(
            product_id=product.id,
            product_name=product.name,
            product_slug=product.slug,
            stores_count=len(store_items),
            stores=store_items,
        )
