"""Consumer discovery, curated occasions, and flavor radar taste matching endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.db.session import get_sync_db
from app.schemas.discovery import (
    DiscoveryFeedResponse,
    OccasionCollection,
    TasteMatchQuery,
    TasteMatchResult,
)
from app.services.discovery_service import DiscoveryService

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.get(
    "/feed",
    response_model=DiscoveryFeedResponse,
    status_code=status.HTTP_200_OK,
    summary="Get consumer discovery feed",
)
def get_discovery_feed(session: Session = Depends(get_sync_db)) -> DiscoveryFeedResponse:
    """Retrieve homepage discovery feed with featured brands, occasion collections, and spotlight spirits."""
    return DiscoveryService.get_discovery_feed(session)


@router.get(
    "/occasions",
    response_model=list[OccasionCollection],
    status_code=status.HTTP_200_OK,
    summary="List all occasion collections",
)
def list_occasions(session: Session = Depends(get_sync_db)) -> list[OccasionCollection]:
    """List all curated occasion collections (Gifting, Peat & Smoke, Indian Craft, etc.)."""
    return DiscoveryService.get_occasions(session)


@router.get(
    "/occasions/{slug}",
    response_model=OccasionCollection,
    status_code=status.HTTP_200_OK,
    summary="Get occasion collection by slug",
)
def get_occasion(slug: str, session: Session = Depends(get_sync_db)) -> OccasionCollection:
    """Retrieve products and story metadata for a specific occasion collection."""
    occasion = DiscoveryService.get_occasion_by_slug(slug, session)
    if not occasion:
        raise ResourceNotFoundError(f"Occasion collection '{slug}' was not found.")
    return occasion


@router.post(
    "/taste-match",
    response_model=list[TasteMatchResult],
    status_code=status.HTTP_200_OK,
    summary="Match spirits by flavor radar profile",
)
def match_taste_profile(
    query: TasteMatchQuery,
    session: Session = Depends(get_sync_db),
) -> list[TasteMatchResult]:
    """Semantic flavor radar matcher calculating cosine similarity against master catalog taste vectors."""
    return DiscoveryService.match_taste_profile(query, session)
