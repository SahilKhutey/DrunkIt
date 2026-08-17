from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/ops/logs",
    tags=["Logs"],
)


@router.get("")
async def get_logs(service: str | None = None, level: str | None = None):
    return [
        {"timestamp": "2026-08-13T10:30:00Z", "level": "INFO", "service": service or "order-service", "event": "order.created", "order_id": "ord_001"},
        {"timestamp": "2026-08-13T10:30:05Z", "level": "INFO", "service": service or "payment-service", "event": "payment.completed", "payment_id": "pay_001"},
    ]
