from fastapi import APIRouter
from services.resilience.app.engine.recovery_engine import RecoveryEngine
from services.resilience.app.schemas.resilience_schemas import RecoveryStartRequest

router = APIRouter(
    prefix="/api/v1/recovery",
    tags=["Recovery"],
)

recovery_engine = RecoveryEngine()


@router.post("/start")
async def start_recovery(payload: RecoveryStartRequest):
    return await recovery_engine.recover(payload.service)


@router.get("/history")
async def recovery_history():
    return [{"service": "order-service", "status": "COMPLETE", "rto_minutes": 12, "rpo_minutes": 3}]
