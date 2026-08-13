from abc import ABC, abstractmethod
from typing import Any


class ComplianceCheck(ABC):

    @abstractmethod
    async def evaluate(self, context: Any) -> dict:
        raise NotImplementedError


class IdentityCheck(ComplianceCheck):

    async def evaluate(self, context: Any) -> dict:
        if not context.consumer_id:
            return {
                "status": "DENY",
                "reason": "Consumer identity unavailable",
            }
        return {"status": "PASS"}


class VerificationCheck(ComplianceCheck):

    def __init__(self, verification_service=None):
        self.verification_service = verification_service

    async def evaluate(self, context: Any) -> dict:
        # Check simulated age / permit verification status
        if getattr(context, "unverified", False):
            return {
                "status": "HOLD",
                "action": "AGE_VERIFICATION_REQUIRED",
            }
        return {"status": "PASS"}


class RetailerLicenceCheck(ComplianceCheck):

    async def evaluate(self, context: Any) -> dict:
        if not context.retailer_id or context.retailer_id.startswith("invalid"):
            return {
                "status": "DENY",
                "reason": "No valid retailer licence",
            }
        return {"status": "PASS"}


class ProductCheck(ComplianceCheck):

    async def evaluate(self, context: Any) -> dict:
        if not context.product_id or context.product_id.startswith("blocked"):
            return {
                "status": "DENY",
                "reason": "Product unavailable or not approved for jurisdiction",
            }
        return {"status": "PASS"}


class LocationCheck(ComplianceCheck):

    async def evaluate(self, context: Any) -> dict:
        if context.delivery_latitude == 0.0 and context.delivery_longitude == 0.0:
            return {
                "status": "DENY",
                "reason": "Delivery location not serviceable",
            }
        return {"status": "PASS"}


class CompliancePipeline:

    def __init__(self, checks: list[ComplianceCheck]):
        self.checks = checks

    async def run(self, context: Any) -> list[dict]:
        results = []
        for check in self.checks:
            result = await check.evaluate(context)
            results.append(result)
            if result.get("status") == "DENY":
                break
        return results
