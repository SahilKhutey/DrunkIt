from fastapi import APIRouter
from services.governance.app.engine.retention_engine import RetentionEngine

router = APIRouter(
    prefix="/api/v1/retention",
    tags=["Retention Policies"],
)

retention_engine = RetentionEngine()


@router.get("/policies")
async def get_retention_policies():
    return [
        {"resource_type": "audit_events", "retention_days": 2555, "deletion_allowed": False},
        {"resource_type": "verification_evidence", "retention_days": 1825, "deletion_allowed": False},
        {"resource_type": "order_checkout", "retention_days": 1095, "deletion_allowed": True},
    ]
