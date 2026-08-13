from fastapi import APIRouter
from services.observability.app.schemas.health_schemas import AlertCreateRequest
from services.observability.app.services.alert_service import AlertService

router = APIRouter(
    prefix="/api/v1/ops/alerts",
    tags=["Alerts"],
)

alert_service = AlertService()


@router.post("")
async def create_alert(payload: AlertCreateRequest):
    return await alert_service.create_alert(
        code=payload.code,
        service=payload.service,
        severity=payload.severity,
        message=payload.message,
    )


@router.get("")
async def get_alerts():
    return await alert_service.get_active_alerts()
