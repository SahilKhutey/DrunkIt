from services.governance.app.engine.evidence_engine import EvidenceEngine


class EvidenceService:

    def __init__(self, evidence_engine: EvidenceEngine | None = None):
        self.evidence_engine = evidence_engine or EvidenceEngine()

    async def create_evidence(
        self,
        evidence_type: str,
        subject_type: str,
        subject_id: str,
        source: str,
        external_reference: str | None = None,
        raw_data: bytes | None = None,
    ) -> dict:

        return await self.evidence_engine.record_evidence(
            evidence_type=evidence_type,
            subject_type=subject_type,
            subject_id=subject_id,
            source=source,
            external_reference=external_reference,
            raw_data=raw_data,
        )

    async def verify_evidence(self, evidence_id: str, raw_data: bytes) -> bool:
        return await self.evidence_engine.verify_evidence(evidence_id, raw_data)
