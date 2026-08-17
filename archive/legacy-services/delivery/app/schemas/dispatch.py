from pydantic import BaseModel, Field


class DispatchQueueRequest(BaseModel):

    delivery_id: str

    priority: int = Field(default=100)


class DispatchJobResponse(BaseModel):

    id: str

    delivery_id: str

    retailer_id: str

    priority: int

    status: str
