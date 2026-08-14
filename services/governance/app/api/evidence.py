from fastapi import APIRouter
from services.governance.app.schemas.governance_schemas import EvidenceCreateRequest
from services.governance.app.services.evidence_service import EvidenceService

router = APIRouter(
    prefix="/api/v1/evidence",
    tags=["Evidence"],
)

evidence_service = EvidenceService()


@router.post("")
async def create_evidence(payload: EvidenceCreateRequest):
    return await evidence_service.create_evidence(
        evidence_type=payload.evidence_type,
        subject_type=payload.subject_type,
        subject_id=payload.subject_id,
        source=payload.source,
        external_reference=payload.external_reference,
    )


@router.get("")
async def list_evidence():
    return list(evidence_service.evidence_engine.evidence_records.values())
