from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/ops/traces",
    tags=["Traces"],
)


@router.get("")
async def get_traces(trace_id: str | None = None):
    tid = trace_id or "trace_abc123"
    return {
        "trace_id": tid,
        "spans": [
            {"service": "api-gateway", "name": "HTTP POST /orders", "duration_ms": 12.0},
            {"service": "order-service", "name": "create_order", "duration_ms": 28.0},
            {"service": "payment-service", "name": "process_payment", "duration_ms": 120.0},
            {"service": "compliance-service", "name": "evaluate_compliance", "duration_ms": 35.0},
            {"service": "security-service", "name": "evaluate_security", "duration_ms": 28.0},
            {"service": "inventory-service", "name": "reserve_stock", "duration_ms": 45.0},
        ],
        "total_duration_ms": 268.0,
    }
