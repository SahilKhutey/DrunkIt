from fastapi import APIRouter, HTTPException
from services.security.app.services.device_service import DeviceService

router = APIRouter(
    prefix="/security/devices",
    tags=["Device Intelligence"],
)

device_service = DeviceService()


@router.get("/{device_id}")
async def get_device(device_id: str):
    dev = await device_service.get_device(device_id)
    if not dev:
        raise HTTPException(status_code=404, detail="DEVICE_NOT_FOUND")
    return dev
