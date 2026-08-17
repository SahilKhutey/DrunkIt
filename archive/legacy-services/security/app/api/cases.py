from fastapi import APIRouter, HTTPException
from services.security.app.schemas.security_schemas import SecurityCaseCreateRequest
from services.security.app.services.case_service import CaseService

router = APIRouter(
    prefix="/security/cases",
    tags=["Security Cases"],
)

case_service = CaseService()


@router.post("")
async def create_case(payload: SecurityCaseCreateRequest):
    return await case_service.create_case(
        subject_type=payload.subject_type,
        subject_id=payload.subject_id,
        category=payload.category,
        priority=payload.priority,
    )


@router.get("")
async def list_cases(status: str | None = None):
    return await case_service.list_cases(status=status)


@router.get("/{case_id}")
async def get_case(case_id: str):
    case = await case_service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="CASE_NOT_FOUND")
    return case
