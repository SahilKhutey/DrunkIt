from fastapi import APIRouter, HTTPException
from services.governance.app.schemas.governance_schemas import PolicyCreateRequest
from services.governance.app.services.policy_service import PolicyService

router = APIRouter(
    prefix="/api/v1/policies",
    tags=["Policies"],
)

policy_service = PolicyService()


@router.post("")
async def create_policy(payload: PolicyCreateRequest):
    return await policy_service.create_policy(
        name=payload.name,
        jurisdiction=payload.jurisdiction,
        scope=payload.scope,
        rules=payload.rules,
    )


@router.get("")
async def list_policies():
    return list(policy_service.policies.values())


@router.post("/{policy_id}/approve")
async def approve_policy(policy_id: str):
    try:
        return await policy_service.transition_status(policy_id, "APPROVED")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{policy_id}/activate")
async def activate_policy(policy_id: str):
    try:
        return await policy_service.transition_status(policy_id, "ACTIVE")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{policy_id}/retire")
async def retire_policy(policy_id: str):
    try:
        return await policy_service.transition_status(policy_id, "RETIRED")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
