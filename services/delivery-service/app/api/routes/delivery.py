from typing import Annotated
from fastapi import APIRouter, Depends
from faccp_common.dto import APIResponse
from app.api.dependencies import get_delivery_service
from app.schemas.delivery import CreateTaskRequest, TaskResponse, VerifyHandoverRequest
from app.services.delivery_service import DeliveryService

router = APIRouter(prefix="/delivery", tags=["Delivery & Dispatch"])


@router.post("/tasks", status_code=201)
async def create_task(
    payload: CreateTaskRequest,
    service: Annotated[DeliveryService, Depends(get_delivery_service)],
) -> APIResponse[TaskResponse]:
    res = await service.create_task(payload)
    return APIResponse(data=res)


@router.post("/verify-handover")
async def verify_handover(
    payload: VerifyHandoverRequest,
    service: Annotated[DeliveryService, Depends(get_delivery_service)],
) -> APIResponse[TaskResponse]:
    res = await service.verify_handover(payload)
    return APIResponse(data=res)
