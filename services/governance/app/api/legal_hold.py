from fastapi import APIRouter
from services.governance.app.api.retention import retention_engine
from services.governance.app.schemas.governance_schemas import LegalHoldCreateRequest

router = APIRouter(
    prefix="/api/v1/legal-holds",
    tags=["Legal Holds"],
)


@router.post("")
async def create_legal_hold(payload: LegalHoldCreateRequest):
    retention_engine.add_legal_hold(payload.subject_id)
    return {
        "name": payload.name,
        "reason": payload.reason,
        "subject_id": payload.subject_id,
        "status": "ACTIVE",
    }


@router.get("")
async def list_legal_holds():
    return list(retention_engine.legal_holds)


@router.post("/{subject_id}/release")
async def release_legal_hold(subject_id: str):
    retention_engine.release_legal_hold(subject_id)
    return {"subject_id": subject_id, "status": "RELEASED"}
