from datetime import datetime, timezone
from fastapi import APIRouter
from services.compliance.app.engine.context import ComplianceContext
from services.compliance.app.engine.decision_engine import DecisionEngine
from services.compliance.app.schemas.compliance_schemas import ComplianceEvaluateRequest
from services.compliance.app.services.audit_service import AuditService
from services.compliance.app.services.consumer_service import ConsumerService
from services.compliance.app.services.policy_service import PolicyService

router = APIRouter(
    prefix="/compliance",
    tags=["Compliance Evaluation"],
)

policy_service = PolicyService()
decision_engine = DecisionEngine(policy_service=policy_service)
audit_service = AuditService()
consumer_service = ConsumerService()


@router.post("/evaluate")
async def evaluate(request: ComplianceEvaluateRequest):
    # Verify consumer status if provided
    consumer_status = "UNVERIFIED"
    if request.consumer_id:
        v = await consumer_service.get_verification(request.consumer_id)
        if v:
            consumer_status = v["status"]

    ctx = ComplianceContext(
        consumer_id=request.consumer_id,
        retailer_id=request.retailer_id,
        rider_id=request.rider_id,
        product_id=request.product_id,
        order_id=request.order_id,
        delivery_id=request.delivery_id,
        jurisdiction_id=request.jurisdiction_id,
        operation=request.operation,
        timestamp=datetime.now(timezone.utc),
    )
    # Attach dynamic consumer verification status attribute for rule engine matching
    setattr(ctx, "consumer_verification_status", consumer_status)

    decision = await decision_engine.decide(ctx)
    subject_id = str(request.order_id or request.consumer_id or request.retailer_id or "system")

    await audit_service.record(
        action="COMPLIANCE_DECISION",
        subject_id=subject_id,
        metadata=decision,
    )
    return decision


@router.post("/decisions")
async def create_decision(request: ComplianceEvaluateRequest):
    return await evaluate(request)
