"""Brand Portal API endpoints for intelligence dashboards, taste radar visualizers, and regional analytics."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_sync_db
from app.models.identity import User
from app.schemas.brand_portal import (
    BrandDashboardResponse,
    BrandRegionalDistribution,
    BrandTasteRadarVisualization,
)
from app.services.brand_portal_service import BrandPortalService

router = APIRouter(prefix="/brand-portal", tags=["brand-portal"])


@router.get(
    "/brands/{brand_id}/dashboard",
    response_model=BrandDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get brand intelligence dashboard",
)
def get_brand_dashboard(
    brand_id: uuid.UUID,
    current_user: User = Depends(require_roles("BRAND_MANAGER", "ADMIN")),
    session: Session = Depends(get_sync_db),
) -> BrandDashboardResponse:
    """Retrieve high-level commercial dashboard, SKU performance, regional distribution, and taste radars for a brand."""
    return BrandPortalService.get_brand_dashboard(brand_id, session)


@router.get(
    "/brands/{brand_id}/taste-radar",
    response_model=list[BrandTasteRadarVisualization],
    status_code=status.HTTP_200_OK,
    summary="Get brand taste radar profiles with category benchmarks",
)
def get_brand_taste_radars(
    brand_id: uuid.UUID,
    session: Session = Depends(get_sync_db),
) -> list[BrandTasteRadarVisualization]:
    """Retrieve 6-axis flavor radar visualizations and peer category benchmark comparisons for all brand expressions."""
    return BrandPortalService.get_brand_taste_radars(brand_id, session)
