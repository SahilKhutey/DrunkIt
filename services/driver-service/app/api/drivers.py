from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session

from app.domain.driver.enums import (
    DriverOperationalStatus,
)

from app.schemas.driver import (
    DriverCreate,
    DriverResponse,
    DriverStatusUpdate,
)

from app.services.driver import (
    DriverService,
)


router = APIRouter(
    prefix="/drivers",
    tags=["Drivers"],
)


@router.post(
    "",
    response_model=DriverResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_driver(
    data: DriverCreate,
    session: AsyncSession = Depends(
        get_session
    ),
):

    service = DriverService(session)

    try:

        return await service.create_driver(
            data
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


@router.get(
    "/{driver_id}",
    response_model=DriverResponse,
)
async def get_driver(
    driver_id: str,
    session: AsyncSession = Depends(
        get_session
    ),
):

    service = DriverService(session)

    driver = await service.repository.get_by_id(
        driver_id
    )

    if not driver:

        raise HTTPException(
            status_code=404,
            detail="Driver not found",
        )

    return driver


@router.post(
    "/{driver_id}/status",
    response_model=DriverResponse,
)
async def change_driver_status(
    driver_id: str,
    data: DriverStatusUpdate,
    session: AsyncSession = Depends(
        get_session
    ),
):

    service = DriverService(session)

    driver = await service.repository.get_by_id(
        driver_id
    )

    if not driver:

        raise HTTPException(
            status_code=404,
            detail="Driver not found",
        )

    try:

        return await service.change_status(
            driver,
            data.status,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc
