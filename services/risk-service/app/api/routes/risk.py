from typing import Annotated
from fastapi import APIRouter, Depends
from faccp_common.dto import APIResponse
from app.api.dependencies import get_risk_service
from app.schemas.risk import RiskEvaluateRequest, RiskEvaluateResponse
from app.services.risk_service import RiskService

router = APIRouter(prefix="/risk", tags=["Risk Assessment"])


@router.post("/evaluate")
async def evaluate_risk(
    payload: RiskEvaluateRequest,
    service: Annotated[RiskService, Depends(get_risk_service)],
) -> APIResponse[RiskEvaluateResponse]:
    res = await service.evaluate_risk(payload)
    return APIResponse(data=res)
