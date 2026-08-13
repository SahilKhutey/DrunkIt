from fastapi import APIRouter, HTTPException
from services.inventory.app.schemas.fulfilment import FulfilmentTransition
from services.inventory.app.services.fulfilment_service import FulfilmentService

router = APIRouter(
    prefix="/fulfilment",
    tags=["Store Fulfilment"],
)

fulfilment_service = FulfilmentService()


@router.post("/{fulfilment_id}/transition")
async def transition_fulfilment(
    fulfilment_id: str,
    payload: FulfilmentTransition,
):
    try:
        return await fulfilment_service.transition(fulfilment_id, payload.target_status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
