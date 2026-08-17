from fastapi import FastAPI
from services.governance.app.api.approvals import router as approvals_router
from services.governance.app.api.audit import router as audit_router
from services.governance.app.api.consent import router as consent_router
from services.governance.app.api.evidence import router as evidence_router
from services.governance.app.api.legal_hold import router as legal_hold_router
from services.governance.app.api.policies import router as policies_router
from services.governance.app.api.reports import router as reports_router
from services.governance.app.api.retention import router as retention_router

app = FastAPI(
    title="Audit, Governance, Policy & Regulatory Control Plane",
    version="1.0.0",
)

app.include_router(audit_router)
app.include_router(policies_router)
app.include_router(evidence_router)
app.include_router(consent_router)
app.include_router(approvals_router)
app.include_router(retention_router)
app.include_router(legal_hold_router)
app.include_router(reports_router)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "governance"}
