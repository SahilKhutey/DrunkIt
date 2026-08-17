from fastapi import APIRouter

from app.schemas.serviceability import (
    ServiceabilityRequest,
)

from app.services.serviceability import (
    ServiceabilityService,
)


router = APIRouter(
    prefix="/serviceability",
    tags=["Serviceability"],
)


@router.post("")
async def check_serviceability(
    request: ServiceabilityRequest,
):

    service = ServiceabilityService()

    return await service.check(
        request
    )
