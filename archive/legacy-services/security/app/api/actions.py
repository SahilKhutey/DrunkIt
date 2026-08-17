from fastapi import APIRouter
from services.security.app.schemas.security_schemas import SecurityActionExecuteRequest
from services.security.app.services.action_service import ActionService

router = APIRouter(
    prefix="/security/actions",
    tags=["Security Actions"],
)

action_service = ActionService()


@router.post("")
async def execute_action(payload: SecurityActionExecuteRequest):
    return await action_service.execute_action(
        action=payload.action,
        subject_type=payload.subject_type,
        subject_id=payload.subject_id,
        reason=payload.reason,
    )
