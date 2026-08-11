from typing import Annotated
from fastapi import APIRouter, Depends
from faccp_common.dto import APIResponse
from app.api.dependencies import get_verification_service
from app.schemas.verification import VerifyDocumentRequest, VerifyDocumentResponse
from app.services.verification_service import VerificationService

router = APIRouter(prefix="/verification", tags=["Identity Verification"])


@router.post("/document")
async def verify_document(
    payload: VerifyDocumentRequest,
    service: Annotated[VerificationService, Depends(get_verification_service)],
) -> APIResponse[VerifyDocumentResponse]:
    res = await service.verify_document(payload)
    return APIResponse(data=res)
