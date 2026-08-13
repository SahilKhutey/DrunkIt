from fastapi import APIRouter, HTTPException
from services.delivery.app.api.dispatch import dispatch_service
from services.delivery.app.schemas.assignment import AssignmentResponse
from services.delivery.app.services.assignment_service import AssignmentService

router = APIRouter(
    prefix="/deliveries",
    tags=["Assignments"],
)

assignment_service = AssignmentService(dispatch_service=dispatch_service)


@router.post("/{delivery_id}/assign", response_model=AssignmentResponse)
async def assign_rider(delivery_id: str):
    try:
        assignment = await assignment_service.assign_rider(delivery_id)
        return AssignmentResponse(
            id=str(assignment["id"]),
            delivery_id=str(assignment["delivery_id"]),
            rider_id=str(assignment["rider_id"]),
            status=assignment["status"],
            distance_meters=assignment.get("distance_meters"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
