from datetime import datetime, timezone

from services.delivery.app.clients.compliance_client import ComplianceClient
from services.delivery.app.schemas.verification import VerificationResult
from services.delivery.app.services.dispatch_service import DispatchService


class VerificationService:

    def __init__(
        self,
        dispatch_service: DispatchService | None = None,
        compliance_client: ComplianceClient | None = None,
    ):
        self.dispatch_service = dispatch_service or DispatchService()
        self.compliance = compliance_client or ComplianceClient()

    async def verify_delivery(
        self,
        delivery_id: str,
        verification_token: str,
    ) -> VerificationResult:

        delivery = self.dispatch_service.deliveries.get(delivery_id)
        if not delivery:
            raise ValueError("DELIVERY_NOT_FOUND")

        if delivery["status"] != "VERIFICATION_PENDING":
            raise ValueError("VERIFICATION_NOT_ALLOWED")

        res = await self.compliance.verify_final_handover(
            delivery_id=delivery_id,
            verification_token=verification_token,
        )

        if res.status != "VERIFIED":
            return VerificationResult(
                delivery_id=delivery_id,
                status="FAILED",
                verification_reference=res.reference,
                verified_at=datetime.now(timezone.utc),
            )

        await self.dispatch_service.transition(delivery, "VERIFIED")

        return VerificationResult(
            delivery_id=delivery_id,
            status="VERIFIED",
            verification_reference=res.reference,
            verified_at=datetime.now(timezone.utc),
        )
