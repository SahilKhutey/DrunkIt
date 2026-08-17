from fastapi import FastAPI

from app.domain.delivery.enums import DeliveryStatus, ActorType
from app.domain.delivery.state_machine import can_transition, validate_transition

app = FastAPI(
    title="Delivery Engine D1 Core",
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "delivery-engine",
        "version": "0.1.0",
        "delivery_statuses": len(DeliveryStatus),
        "actor_types": len(ActorType),
    }
