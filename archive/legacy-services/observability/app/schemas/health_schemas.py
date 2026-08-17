from typing import Literal
from pydantic import BaseModel


class HealthResponse(BaseModel):

    service: str

    status: Literal["healthy", "degraded", "unhealthy"]

    version: str = "1.0.0"

    environment: str = "production"

    checks: dict[str, bool] | None = None


class AlertCreateRequest(BaseModel):

    code: str

    service: str

    severity: str = "HIGH"

    message: str = ""


class IncidentCreateRequest(BaseModel):

    service: str

    title: str

    severity: str = "HIGH"

    assigned_to: str | None = None
