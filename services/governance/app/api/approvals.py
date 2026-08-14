from fastapi import APIRouter, HTTPException
from services.governance.app.schemas.governance_schemas import ApprovalCreateRequest
from services.governance.app.services.approval_service import ApprovalService

router = APIRouter(
    prefix="/api/v1/approvals",
    tags=["Approvals Workflow"],
)

approval_service = ApprovalService()


@router.post("")
async def create_approval(payload: ApprovalCreateRequest, actor: str = "operator_a"):
    return await approval_service.create_request(
        actor=actor,
        action=payload.action,
        resource_type=payload.resource_type,
        resource_id=payload.resource_id,
        risk_level=payload.risk_level,
    )


@router.get("")
async def list_approvals():
    return list(approval_service.approval_engine.requests.values())


@router.post("/{request_id}/approve")
async def approve_request(request_id: str, approver: str = "operator_b"):
    try:
        return await approval_service.approve_request(request_id, approver)
    except (ValueError, PermissionError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
