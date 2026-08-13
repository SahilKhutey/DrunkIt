from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class VerificationRequest(BaseModel):

    verification_token: str


class VerificationResult(BaseModel):

    delivery_id: str

    status: Literal["VERIFIED", "FAILED", "REQUIRES_REVIEW"]

    verification_reference: str

    verified_at: datetime
