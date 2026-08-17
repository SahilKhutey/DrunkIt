from fastapi import APIRouter
from services.security.app.api.risk import risk_service

router = APIRouter(
    prefix="/security/signals",
    tags=["Risk Signals"],
)


@router.get("/{subject_type}/{subject_id}")
async def get_signals(subject_type: str, subject_id: str):
    return await risk_service.get_signals(subject_type, subject_id)
