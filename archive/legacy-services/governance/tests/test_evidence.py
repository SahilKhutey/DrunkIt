import pytest
from services.governance.app.services.evidence_service import EvidenceService


@pytest.mark.asyncio
async def test_evidence_creation_and_verification():
    svc = EvidenceService()
    raw = b"license_document_data_bytes"
    ev = await svc.create_evidence(
        evidence_type="RETAILER_LICENSE",
        subject_type="RETAILER",
        subject_id="ret-1001",
        source="STATE_EXCISE_API",
        external_reference="lic_ref_99",
        raw_data=raw,
    )

    assert ev["evidence_id"].startswith("ev_")
    assert await svc.verify_evidence(ev["evidence_id"], raw) is True
    assert await svc.verify_evidence(ev["evidence_id"], b"corrupted") is False
