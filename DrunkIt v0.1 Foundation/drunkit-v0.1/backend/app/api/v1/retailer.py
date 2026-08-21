"""Retailer network, inventory management, pricing, and live availability endpoints."""

import uuid
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.exceptions import ResourceNotFoundError
from app.db.session import get_sync_db
from app.db.uow import SyncUnitOfWork
from app.models.identity import User
from app.schemas.retailer import (
    InventorySnapshotCreate,
    InventorySnapshotResponse,
    PriceCreate,
    PriceResponse,
    ProductAvailabilityResponse,
    RetailerCreate,
    RetailerLicenceCreate,
    RetailerLicenceResponse,
    RetailerLocationCreate,
    RetailerLocationResponse,
    RetailerResponse,
    RetailerSKUMapRequest,
    RetailerSKUResponse,
)
from app.services.retailer_service import RetailerService

router = APIRouter(tags=["retailer"])


# ──────────────────────────────────────────────────────────────────────────────
# 1. Retailer Lifecycle Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/retailers",
    response_model=list[RetailerResponse],
    status_code=status.HTTP_200_OK,
    summary="List all registered retailers",
)
def list_retailers(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_roles("ADMIN", "RETAILER")),
    session: Session = Depends(get_sync_db),
) -> list[RetailerResponse]:
    """Retrieve list of licensed alcohol retailers and off-shops."""
    retailers = RetailerService.list_retailers(limit=limit, offset=offset, session=session)
    return [RetailerResponse.model_validate(r) for r in retailers]


@router.get(
    "/retailers/{retailer_id}",
    response_model=RetailerResponse,
    status_code=status.HTTP_200_OK,
    summary="Get retailer profile",
)
def get_retailer(
    retailer_id: uuid.UUID,
    session: Session = Depends(get_sync_db),
) -> RetailerResponse:
    """Retrieve retailer profile details."""
    retailer = RetailerService.get_retailer(retailer_id, session)
    if not retailer:
        raise ResourceNotFoundError(f"Retailer '{retailer_id}' was not found.")
    return RetailerResponse.model_validate(retailer)


@router.post(
    "/retailers",
    response_model=RetailerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Onboard a new retailer (Admin/Retailer only)",
)
def create_retailer(
    request: RetailerCreate,
    current_user: User = Depends(require_roles("ADMIN", "RETAILER")),
    session: Session = Depends(get_sync_db),
) -> RetailerResponse:
    """Register a new retailer organization."""
    uow = SyncUnitOfWork(session)
    with uow:
        retailer = RetailerService.create_retailer(
            data=request,
            uow=uow,
            actor_id=current_user.id,
        )
    return RetailerResponse.model_validate(retailer)


@router.post(
    "/retailers/{retailer_id}/locations",
    response_model=RetailerLocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a physical store location for a retailer",
)
def create_location(
    retailer_id: uuid.UUID,
    request: RetailerLocationCreate,
    current_user: User = Depends(require_roles("ADMIN", "RETAILER")),
    session: Session = Depends(get_sync_db),
) -> RetailerLocationResponse:
    """Register a physical store or warehouse location."""
    location = RetailerService.create_location(retailer_id, request, session)
    session.commit()
    return RetailerLocationResponse.model_validate(location)


@router.post(
    "/retailers/{retailer_id}/licences",
    response_model=RetailerLicenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register an excise licence for a retailer",
)
def create_licence(
    retailer_id: uuid.UUID,
    request: RetailerLicenceCreate,
    current_user: User = Depends(require_roles("ADMIN", "RETAILER")),
    session: Session = Depends(get_sync_db),
) -> RetailerLicenceResponse:
    """Submit and bind a valid state excise licence to a retailer entity."""
    licence = RetailerService.create_licence(retailer_id, request, session)
    session.commit()
    return RetailerLicenceResponse.model_validate(licence)


# ──────────────────────────────────────────────────────────────────────────────
# 2. Inventory & POS Mapping Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@router.post(
    "/retailers/locations/{location_id}/skus/map",
    response_model=RetailerSKUResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Map a store POS SKU to a canonical SKU",
)
def map_sku(
    location_id: uuid.UUID,
    request: RetailerSKUMapRequest,
    current_user: User = Depends(require_roles("ADMIN", "RETAILER")),
    session: Session = Depends(get_sync_db),
) -> RetailerSKUResponse:
    """Bind a store-level barcode/inventory code to a canonical DrunkIt SKU."""
    uow = SyncUnitOfWork(session)
    with uow:
        ret_sku = RetailerService.map_sku(location_id, request, uow)
    return RetailerSKUResponse.model_validate(ret_sku)


@router.post(
    "/retailers/locations/{location_id}/inventory/snapshot",
    response_model=InventorySnapshotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest an inventory snapshot for a store SKU",
)
def ingest_inventory_snapshot(
    location_id: uuid.UUID,
    request: InventorySnapshotCreate,
    current_user: User = Depends(require_roles("ADMIN", "RETAILER")),
    session: Session = Depends(get_sync_db),
) -> InventorySnapshotResponse:
    """Ingest POS inventory level and availability status."""
    uow = SyncUnitOfWork(session)
    with uow:
        snapshot = RetailerService.ingest_inventory_snapshot(request, uow)
    return InventorySnapshotResponse.model_validate(snapshot)


@router.post(
    "/retailers/locations/{location_id}/prices",
    response_model=PriceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Set or update active price for a store SKU",
)
def set_price(
    location_id: uuid.UUID,
    request: PriceCreate,
    current_user: User = Depends(require_roles("ADMIN", "RETAILER")),
    session: Session = Depends(get_sync_db),
) -> PriceResponse:
    """Publish temporal pricing for a retailer SKU."""
    uow = SyncUnitOfWork(session)
    with uow:
        price = RetailerService.set_price(request, uow)
    return PriceResponse.model_validate(price)


# ──────────────────────────────────────────────────────────────────────────────
# 3. Live Availability Consumer Discovery Endpoint
# ──────────────────────────────────────────────────────────────────────────────

@router.get(
    "/products/{product_id}/availability",
    response_model=ProductAvailabilityResponse,
    status_code=status.HTTP_200_OK,
    summary="Get live localized store availability and pricing for a product",
)
def get_product_availability(
    product_id: str,
    latitude: float | None = Query(default=None, description="Consumer latitude for proximity sort"),
    longitude: float | None = Query(default=None, description="Consumer longitude for proximity sort"),
    state_code: str | None = Query(default=None, description="State code filter (e.g. IN-WB or WB)"),
    city: str | None = Query(default=None, description="City filter (e.g. Kolkata)"),
    session: Session = Depends(get_sync_db),
) -> ProductAvailabilityResponse:
    """Compute real-time store availability, distance, stock levels, and active pricing for a product."""
    # Normalize state_code if passed as "IN-WB" -> "WB"
    normalized_state = state_code
    if normalized_state and normalized_state.upper().startswith("IN-"):
        normalized_state = normalized_state.upper().replace("IN-", "")

    return RetailerService.get_product_availability(
        product_identifier=product_id,
        latitude=latitude,
        longitude=longitude,
        state_code=normalized_state,
        city=city,
        session=session,
    )
