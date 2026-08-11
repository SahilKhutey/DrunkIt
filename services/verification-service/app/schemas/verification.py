from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class VerifyDocumentRequest(BaseModel):
    consumer_id: str
    document_type: str
    document_number: str


class VerifyDocumentResponse(BaseModel):
    id: str
    consumer_id: str
    document_type: str
    status: str
    confidence: float
    verified_at: datetime | None
