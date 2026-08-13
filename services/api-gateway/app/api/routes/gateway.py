"""API Gateway routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from faccp_common.dto import SuccessResponse

from app.api.dependencies import get_gateway_service
from app.schemas.gateway import GatewayHealthSummary, ServiceRouteInfo
from app.services.gateway_service import GatewayService

router = APIRouter(prefix="/gateway", tags=["Unified Reverse Proxy"])


@router.get("/routes", response_model=SuccessResponse[list[ServiceRouteInfo]])
async def get_routes(
    service: Annotated[GatewayService, Depends(get_gateway_service)],
) -> SuccessResponse[list[ServiceRouteInfo]]:
    routes = service.get_routes()
    return SuccessResponse(data=routes, message="Gateway active routes")


@router.get("/health-all", response_model=SuccessResponse[GatewayHealthSummary])
async def get_health_all(
    service: Annotated[GatewayService, Depends(get_gateway_service)],
) -> SuccessResponse[GatewayHealthSummary]:
    summary = await service.get_health_summary()
    return SuccessResponse(data=summary, message="Gateway downstream service health summary")
