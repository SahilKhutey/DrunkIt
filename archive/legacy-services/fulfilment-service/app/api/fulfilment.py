from fastapi import (
    APIRouter,
    HTTPException,
)

from app.domain.fulfilment.planner import (
    FulfilmentPlanner,
)

from app.schemas.fulfilment import (
    FulfilmentRequest,
)


router = APIRouter(
    prefix="/fulfilment",
    tags=["Fulfilment"],
)


@router.post("/plan")
async def create_fulfilment_plan(
    request: FulfilmentRequest,
):

    planner = FulfilmentPlanner()

    try:

        return await planner.create_plan(
            request
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc
