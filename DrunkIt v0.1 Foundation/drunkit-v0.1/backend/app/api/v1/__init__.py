"""API v1 router registry for DrunkIt v0.1."""

from typing import Any
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.brand_portal import router as brand_portal_router
from app.api.v1.catalog import router as catalog_router
from app.api.v1.commerce import router as commerce_router
from app.api.v1.compliance import router as compliance_router
from app.api.v1.delivery import router as delivery_router
from app.api.v1.discovery import router as discovery_router
from app.api.v1.retailer import router as retailer_router
from app.api.v1.retailer_portal import router as retailer_portal_router

api_v1_router = APIRouter(prefix="/api/v1")


@api_v1_router.get("", tags=["system"])
def api_v1_root() -> dict[str, Any]:
    """API v1 root descriptor endpoint."""
    return {
        "name": "DrunkIt API",
        "version": "v1",
        "status": "active",
        "surfaces": [
            "consumer",
            "retailer",
            "brands",
            "intelligence",
            "compliance",
            "delivery",
        ],
    }


api_v1_router.include_router(auth_router)
api_v1_router.include_router(brand_portal_router)
api_v1_router.include_router(catalog_router)
api_v1_router.include_router(commerce_router)
api_v1_router.include_router(compliance_router)
api_v1_router.include_router(delivery_router)
api_v1_router.include_router(discovery_router)
api_v1_router.include_router(retailer_router)
api_v1_router.include_router(retailer_portal_router)

__all__ = ["api_v1_router"]
