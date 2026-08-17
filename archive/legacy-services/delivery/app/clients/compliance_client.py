from datetime import datetime, timezone


class VerificationClientResponse:

    def __init__(self, status: str, reference: str):
        self.status = status
        self.reference = reference
        self.verified_at = datetime.now(timezone.utc)


class ComplianceClient:

    def __init__(self, http=None):
        self.http = http

    async def verify_final_handover(
        self,
        delivery_id: str,
        verification_token: str,
    ) -> VerificationClientResponse:

        if verification_token == "invalid_token":
            return VerificationClientResponse(status="FAILED", reference="ref_failed")
        return VerificationClientResponse(status="VERIFIED", reference=f"ref_v_{delivery_id}")
