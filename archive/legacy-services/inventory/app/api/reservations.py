from fastapi import APIRouter, HTTPException
from services.inventory.app.api.inventory import inventory_service
from services.inventory.app.schemas.reservation import ReservationCreate
from services.inventory.app.services.reservation_service import ReservationService

router = APIRouter(
    prefix="/reservations",
    tags=["Reservations"],
)

reservation_service = ReservationService(inventory_service=inventory_service)


@router.post("")
async def reserve(payload: ReservationCreate):
    try:
        return await reservation_service.reserve(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{reservation_id}/release")
async def release(reservation_id: str):
    try:
        return await reservation_service.release(reservation_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/{reservation_id}/confirm")
async def confirm(reservation_id: str):
    try:
        return await reservation_service.confirm(reservation_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
