from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.delivery.enums import DeliveryStatus


class DeliveryCreate(BaseModel):
    order_id: str = Field(min_length=1)
    retailer_id: str = Field(default="ret_default")
    store_id: str = Field(min_length=1)
    consumer_id: str = Field(min_length=1)

    pickup_address: str = Field(min_length=1)
    dropoff_address: str = Field(min_length=1)


class DeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    order_id: str
    retailer_id: str
    store_id: str
    consumer_id: str
    driver_id: str | None
    pickup_address: str
    dropoff_address: str
    status: DeliveryStatus
    created_at: datetime
    updated_at: datetime


class StatusTransitionRequest(BaseModel):
    target_status: DeliveryStatus


class DriverAssignmentRequest(BaseModel):
    driver_id: str = Field(min_length=1)


# Compatibility aliases
MissionCreate = DeliveryCreate
DriverAssignRequest = DriverAssignmentRequest


class LocationPingRequest(BaseModel):
    driver_id: str = Field(default="drv_123")
    latitude: float = Field(default=12.9716)
    longitude: float = Field(default=77.5946)


class DeliveryCompleteRequest(BaseModel):
    proof_token: str = Field(default="pod_token_123")
    otp: str = Field(default="1234")


