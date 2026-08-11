import time
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import ComplianceEvaluationRequest, ComplianceDecisionResponse
from .engine import evaluate_compliance

app = FastAPI(
    title="FACCP Regulatory Compliance Engine",
    description="Declarative Jurisdiction-Aware Policy Evaluation Microservice",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "compliance-service"}

@app.post("/api/v1/compliance/evaluate", response_model=ComplianceDecisionResponse)
def evaluate(req: ComplianceEvaluationRequest):
    result, reasons, policy_version = evaluate_compliance(req)
    decision_id = f"DEC-{uuid.uuid4().hex[:8].upper()}"

    return ComplianceDecisionResponse(
        decision_id=decision_id,
        result=result,
        jurisdiction=req.jurisdiction,
        policy_version=policy_version,
        reasons=reasons,
        evaluated_at=str(int(time.time()))
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
