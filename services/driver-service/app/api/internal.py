from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session

from app.repositories.driver import (
    DriverRepository,
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
