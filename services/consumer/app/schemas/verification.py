"""Consumer verification schemas."""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel
from ..domain.enums import VerificationMethod, VerificationStatus


class VerificationRequest(BaseModel):
    method: VerificationMethod


class VerificationResult(BaseModel):
    status: VerificationStatus
    provider_reference: str | None = None
    verified_at: datetime | None = None
    expires_at: datetime | None = None
