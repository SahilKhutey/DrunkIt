from fastapi import APIRouter
from services.governance.app.schemas.governance_schemas import AuditEventRecordRequest
from services.governance.app.services.audit_service import AuditService

router = APIRouter(
    prefix="/api/v1/audit",
    tags=["Audit Trails"],
)

audit_service = AuditService()


@router.post("/events")
async def record_event(payload: AuditEventRecordRequest):
    return await audit_service.record_event(payload.model_dump())


@router.get("/events")
async def get_events(subject_id: str | None = None, correlation_id: str | None = None):
    return await audit_service.get_events(subject_id=subject_id, correlation_id=correlation_id)


@router.get("/subject/{subject_id}")
async def get_subject_audit(subject_id: str):
    return await audit_service.get_events(subject_id=subject_id)


@router.get("/correlation/{correlation_id}")
async def get_correlation_audit(correlation_id: str):
    return await audit_service.get_events(correlation_id=correlation_id)


@router.get("/verify")
async def verify_chain():
    return {"chain_valid": await audit_service.verify_audit_chain()}
