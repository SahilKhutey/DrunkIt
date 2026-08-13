from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session

from app.repositories.driver import (
    DriverRepository,
)

from app.schemas.driver import (
    DriverReservationRequest,
)


router = APIRouter(
    prefix="/internal/drivers",
    tags=["Internal Drivers"],
)


@router.get("/available")
async def available_drivers(
    session: AsyncSession = Depends(
        get_session
    ),
):

    repository = DriverRepository(
        session
    )

    drivers = await repository.get_available_drivers()

    return {
        "drivers": [
            {
                "driver_id": driver.id,
                "vehicle_type": (
                    driver.vehicle_type.value
                ),
                "latitude": driver.latitude,
                "longitude": driver.longitude,
            }
            for driver in drivers
        ]
    }


@router.post(
    "/{driver_id}/reserve"
)
async def reserve_driver(
    driver_id: str,
    request: DriverReservationRequest,
    session: AsyncSession = Depends(
        get_session
    ),
):

    repository = DriverRepository(
        session
    )

    success = await repository.reserve_driver(
        driver_id
    )

    if not success:

        raise HTTPException(
            status_code=409,
            detail=(
                "Driver is no longer available"
            ),
        )

    return {
        "driver_id": driver_id,
        "delivery_id": request.delivery_id,
        "status": "RESERVED",
    }
