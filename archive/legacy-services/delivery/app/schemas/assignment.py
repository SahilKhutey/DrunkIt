from pydantic import BaseModel


class RiderAssignmentRequest(BaseModel):

    delivery_id: str


class AssignmentResponse(BaseModel):

    id: str

    delivery_id: str

    rider_id: str

    status: str

    distance_meters: int | None = None
