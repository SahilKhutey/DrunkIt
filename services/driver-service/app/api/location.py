from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session

from app.schemas.driver import (
    DriverLocationUpdate,
)

from app.services.location import (
    LocationService,
)

from app.repositories.driver import (
    DriverRepository,
)


router = APIRouter(
    prefix="/drivers",
    tags=["Driver Location"],
)


@router.post(
    "/{driver_id}/location"
)
async def update_location(
    driver_id: str,
    data: DriverLocationUpdate,
    session: AsyncSession = Depends(
        get_session
    ),
):

    repository = DriverRepository(
        session
    )

    driver = await repository.get_by_id(
        driver_id
    )

    if not driver:

        raise HTTPException(
            status_code=404,
            detail="Driver not found",
        )

    service = LocationService(
        session
    )

    try:

        driver = await service.update_location(
            driver,
            data,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    return {
        "driver_id": driver.id,
        "latitude": driver.latitude,
        "longitude": driver.longitude,
        "updated_at": driver.location_updated_at,
    }
