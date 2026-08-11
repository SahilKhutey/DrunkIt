from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from faccp_common.security import FieldEncryption, pseudonymize
from app.config import get_settings
from app.db.models import VerificationRequest
from app.schemas.verification import VerifyDocumentRequest, VerifyDocumentResponse


class VerificationService:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.settings = get_settings()
        self.enc = FieldEncryption(self.settings.field_encryption_key)

    async def verify_document(self, req: VerifyDocumentRequest) -> VerifyDocumentResponse:
        doc_hash = pseudonymize(req.document_number)
        enc_doc = self.enc.encrypt(req.document_number)

        record = VerificationRequest(
            consumer_id=req.consumer_id,
            document_type=req.document_type,
            document_number_encrypted=enc_doc,
            document_hash=doc_hash,
            status="SUCCESS",
            confidence=0.99,
            verified_at=datetime.now(timezone.utc),
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)

        return VerifyDocumentResponse(
            id=record.id,
            consumer_id=record.consumer_id,
            document_type=record.document_type,
            status=record.status,
            confidence=record.confidence,
            verified_at=record.verified_at,
        )
