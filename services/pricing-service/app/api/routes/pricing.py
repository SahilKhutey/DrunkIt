from typing import Annotated
from fastapi import APIRouter, Depends
from faccp_common.dto import APIResponse
from app.api.dependencies import get_pricing_service
from app.schemas.pricing import (
    CalculateRequest, CalculateResponse, CreatePriceBookRequest, CreatePromotionRequest,
)
from app.services.pricing_service import PricingService

router = APIRouter(prefix="/pricing", tags=["Pricing"])


@router.post("/price-books", status_code=201)
async def create_price_book(
    payload: CreatePriceBookRequest,
    service: Annotated[PricingService, Depends(get_pricing_service)],
) -> APIResponse[dict]:
    pb = await service.create_price_book(payload)
    return APIResponse(data={"id": pb.id, "name": pb.name, "store_id": pb.store_id})


@router.post("/promotions", status_code=201)
async def create_promotion(
    payload: CreatePromotionRequest,
    service: Annotated[PricingService, Depends(get_pricing_service)],
) -> APIResponse[dict]:
    p = await service.create_promotion(payload)
    return APIResponse(data={"id": p.id, "code": p.code, "discount_type": p.discount_type, "discount_value": str(p.discount_value)})


@router.post("/calculate")
async def calculate(
    payload: CalculateRequest,
    service: Annotated[PricingService, Depends(get_pricing_service)],
) -> APIResponse[CalculateResponse]:
    result = await service.calculate(payload)
    return APIResponse(data=result)
