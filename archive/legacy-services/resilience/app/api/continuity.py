from fastapi import APIRouter
from services.resilience.app.schemas.resilience_schemas import EmergencyActionRequest
from services.resilience.app.services.continuity_service import ContinuityService

router = APIRouter(
    prefix="/api/v1/continuity",
    tags=["Business Continuity"],
)

continuity_service = ContinuityService()


@router.get("/status")
async def continuity_status():
    return await continuity_service.get_status()


@router.post("/emergency/enable")
async def enable_emergency(payload: EmergencyActionRequest):
    return await continuity_service.enable_emergency(actor=payload.actor, reason=payload.reason)


@router.post("/emergency/disable")
async def disable_emergency(payload: EmergencyActionRequest):
    return await continuity_service.disable_emergency(actor=payload.actor)
