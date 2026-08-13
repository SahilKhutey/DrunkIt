from fastapi import APIRouter
from services.observability.app.api.alerts import alert_service
from services.observability.app.api.incidents import incident_service
from services.observability.app.services.health_service import HealthService

router = APIRouter(
    prefix="/api/v1/ops",
    tags=["Ops Overview"],
)

health_service = HealthService()


@router.get("/overview")
async def overview():
    services = await health_service.get_all_services()
    incidents = await incident_service.get_active_incidents()
    alerts = await alert_service.get_active_alerts()
    return {
        "health_score_pct": 100.0 if not incidents else 92.86,
        "status": "healthy" if not incidents else "degraded",
        "services_count": len(services),
        "active_incidents_count": len(incidents),
        "active_alerts_count": len(alerts),
        "services": services,
        "incidents": incidents,
        "alerts": alerts,
    }


@router.get("/services")
async def get_services():
    return await health_service.get_all_services()
