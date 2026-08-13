from fastapi import APIRouter, HTTPException
from services.compliance.app.api.decisions import policy_service

router = APIRouter(
    prefix="/compliance/policies",
    tags=["Policy Management"],
)


@router.get("/{jurisdiction_id}")
async def get_policy(jurisdiction_id: str, operation: str = "CREATE_ALCOHOL_ORDER"):
    policy = await policy_service.get_policy(jurisdiction_id, operation)
    if not policy:
        raise HTTPException(status_code=404, detail="POLICY_NOT_FOUND")
    return {
        "id": policy.id,
        "policy_code": policy.policy_code,
        "jurisdiction_id": policy.jurisdiction_id,
        "version": policy.version,
        "status": policy.status,
        "rules": policy.rules,
    }
