from fastapi import APIRouter
from services.compliance.app.api.decisions import audit_service

router = APIRouter(
    prefix="/compliance/audits",
    tags=["Compliance Audits"],
)


@router.get("/{subject_id}")
async def get_audits(subject_id: str):
    return await audit_service.get_audits(subject_id)
