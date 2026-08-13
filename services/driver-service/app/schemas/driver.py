from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.driver.enums import (
    DriverAccountStatus,
    DriverOperationalStatus,
    VehicleType,
    VerificationStatus,
)


class DriverCreate(BaseModel):

    user_id: str = Field(min_length=1)

    name: str = Field(
        min_length=2,
        max_length=200,
    )

    phone: str = Field(
        min_length=5,
        max_length=30,
    )

    vehicle_type: VehicleType


class DriverResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: str
    user_id: str
    name: str
    phone: str

    account_status: DriverAccountStatus

    operational_status: DriverOperationalStatus

    verification_status: VerificationStatus

    vehicle_type: VehicleType

    latitude: float | None
    longitude: float | None

    location_updated_at: datetime | None


class DriverStatusUpdate(BaseModel):

    status: DriverOperationalStatus


class DriverLocationUpdate(BaseModel):

    latitude: float = Field(
        ge=-90,
        le=90,
    )

    longitude: float = Field(
        ge=-180,
        le=180,
    )

    accuracy_meters: float | None = Field(
        default=None,
        ge=0,
    )
