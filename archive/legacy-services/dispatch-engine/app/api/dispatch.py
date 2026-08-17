from fastapi import (
    APIRouter,
    HTTPException,
)

from app.schemas.dispatch import (
    DispatchRequest,
)

from app.services.dispatch import (
    DispatchService,
)


router = APIRouter(
    prefix="/dispatch",
    tags=["Dispatch"],
)


@router.post("")
async def dispatch_delivery(
    request: DispatchRequest,
):

    service = DispatchService()

    try:

        return await service.dispatch(
            request
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"Dispatch failed: {exc}",
        ) from exc
