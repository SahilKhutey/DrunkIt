from fastapi import APIRouter, HTTPException
from services.security.app.schemas.security_schemas import SessionRevokeRequest
from services.security.app.services.session_service import SessionService

router = APIRouter(
    prefix="/security/sessions",
    tags=["Session Security"],
)

session_service = SessionService()


@router.post("/revoke")
async def revoke_session(payload: SessionRevokeRequest):
    try:
        return await session_service.revoke_session(payload.session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
