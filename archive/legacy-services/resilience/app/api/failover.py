from fastapi import APIRouter
from services.resilience.app.schemas.resilience_schemas import FailoverExecuteRequest
from services.resilience.app.services.failover_service import FailoverService

router = APIRouter(
    prefix="/api/v1/failover",
    tags=["Failover"],
)

failover_service = FailoverService()


@router.get("/status")
async def failover_status(service: str = "order-service"):
    return await failover_service.get_failover_status(service)


@router.post("/execute")
async def execute_failover(payload: FailoverExecuteRequest):
    return await failover_service.execute_failover(
        service=payload.service,
        primary=payload.primary,
        secondary=payload.secondary,
    )
