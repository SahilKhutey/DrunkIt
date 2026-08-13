from fastapi import APIRouter, HTTPException
from services.observability.app.schemas.health_schemas import IncidentCreateRequest
from services.observability.app.services.incident_service import IncidentService

router = APIRouter(
    prefix="/api/v1/ops/incidents",
    tags=["Incidents"],
)

incident_service = IncidentService()


@router.post("")
async def create_incident(payload: IncidentCreateRequest):
    return await incident_service.create_incident(
        service=payload.service,
        title=payload.title,
        severity=payload.severity,
        assigned_to=payload.assigned_to,
    )


@router.get("")
async def get_incidents():
    return await incident_service.get_active_incidents()


@router.get("/{incident_id}")
async def get_incident(incident_id: str):
    inc = await incident_service.get_incident(incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="INCIDENT_NOT_FOUND")
    return inc


@router.post("/{incident_id}/acknowledge")
async def acknowledge_incident(incident_id: str):
    try:
        return await incident_service.acknowledge_incident(incident_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/{incident_id}/resolve")
async def resolve_incident(incident_id: str):
    try:
        return await incident_service.resolve_incident(incident_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
