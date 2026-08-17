from fastapi import APIRouter, HTTPException
from services.governance.app.engine.consent_engine import ConsentEngine
from services.governance.app.schemas.governance_schemas import ConsentGrantRequest

router = APIRouter(
    prefix="/api/v1/consent",
    tags=["Consent Registry"],
)

consent_engine = ConsentEngine()


@router.post("")
async def grant_consent(payload: ConsentGrantRequest):
    return await consent_engine.grant_consent(
        subject_id=payload.subject_id,
        consent_type=payload.consent_type,
        version=payload.version,
        source=payload.source,
    )


@router.get("/{subject_id}")
async def get_consent(subject_id: str, consent_type: str = "TERMS_AND_CONDITIONS"):
    has_valid = await consent_engine.has_valid_consent(subject_id, consent_type)
    return {"subject_id": subject_id, "consent_type": consent_type, "has_valid_consent": has_valid}


@router.post("/{subject_id}/withdraw")
async def withdraw_consent(subject_id: str, consent_type: str = "TERMS_AND_CONDITIONS"):
    try:
        return await consent_engine.withdraw_consent(subject_id, consent_type)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
