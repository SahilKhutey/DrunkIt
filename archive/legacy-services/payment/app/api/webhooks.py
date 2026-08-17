from fastapi import APIRouter, Header, HTTPException, Request
from services.payment.app.gateways.mock import MockGateway

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)

gateway = MockGateway()
processed_events: set[str] = set()


@router.post("/payment")
async def payment_webhook(
    request: Request,
    x_payment_signature: str | None = Header(None, alias="X-Payment-Signature"),
):
    body = await request.body()
    if not x_payment_signature:
        raise HTTPException(status_code=400, detail="MISSING_SIGNATURE")

    try:
        gateway.verify_webhook(body, x_payment_signature)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    data = await request.json()
    event_id = data.get("event_id")
    if event_id in processed_events:
        return {"status": "already_processed"}

    processed_events.add(event_id)
    return {"received": True, "event_id": event_id}
