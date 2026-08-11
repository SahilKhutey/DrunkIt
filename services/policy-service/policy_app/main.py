import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .models import EvaluatePolicyRequest, EvaluatePolicyResponse, BreakGlassLevel
from .rbac_matrix import check_rbac_permission
from .abac_rules import evaluate_abac_rules
from .sod_detector import record_user_action

app = FastAPI(
    title="FACCP Master ABAC Policy Engine Service",
    description="Role & Attribute-Based Permission Resolution, SoD Enforcement & Break-Glass Authority Microservice",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecordActionRequest(BaseModel):
    user_id: str
    resource_id: str
    action: str

class BreakGlassRequest(BaseModel):
    user_id: str
    level: BreakGlassLevel
    reason: str

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "policy-service", "version": "2.0.0"}

@app.post("/api/v1/policies/evaluate", response_model=EvaluatePolicyResponse)
def evaluate_policy(req: EvaluatePolicyRequest):
    now_iso = req.environment.timestamp_iso or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Step 1: RBAC coarse check
    rbac_allowed = check_rbac_permission(req.subject.role, req.resource.resource_type, req.action)
    if not rbac_allowed:
        return EvaluatePolicyResponse(
            decision="DENY",
            rule_id="RBAC_MATRIX_DENY",
            reason=f"Role '{req.subject.role}' does not have RBAC permission '{req.action}' on resource type '{req.resource.resource_type}'",
            requires_step_up_mfa=False,
            evaluated_at_iso=now_iso
        )

    # Step 2-4: ABAC & SoD & Device Trust Checks
    decision, rule_id, reason, step_up = evaluate_abac_rules(req)

    return EvaluatePolicyResponse(
        decision=decision,
        rule_id=rule_id,
        reason=reason,
        requires_step_up_mfa=step_up,
        evaluated_at_iso=now_iso
    )

@app.post("/api/v1/policies/sod-record")
def record_sod_action(req: RecordActionRequest):
    record_user_action(req.user_id, req.resource_id, req.action)
    return {"status": "recorded", "user_id": req.user_id, "resource_id": req.resource_id, "action": req.action}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
