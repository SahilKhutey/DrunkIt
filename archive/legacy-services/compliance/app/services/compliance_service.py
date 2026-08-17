from services.compliance.app.checks.pipeline import (
    CompliancePipeline,
    IdentityCheck,
    LocationCheck,
    ProductCheck,
    RetailerLicenceCheck,
    VerificationCheck,
)
from services.compliance.app.schemas.compliance import ComplianceContext, ComplianceDecision
from services.compliance.app.services.decision_engine import DecisionEngine


class ComplianceService:

    def __init__(
        self,
        decision_engine: DecisionEngine | None = None,
    ):
        self.decision_engine = decision_engine or DecisionEngine()
        self.pipeline = CompliancePipeline(
            checks=[
                IdentityCheck(),
                VerificationCheck(),
                RetailerLicenceCheck(),
                ProductCheck(),
                LocationCheck(),
            ]
        )

    async def evaluate(
        self,
        context: ComplianceContext,
    ) -> ComplianceDecision:

        checks = await self.pipeline.run(context)
        decision_dict = await self.decision_engine.decide(checks)

        return ComplianceDecision(
            decision=decision_dict["decision"],
            reasons=decision_dict["reasons"],
            required_actions=decision_dict["required_actions"],
            policy_version=decision_dict.get("policy_version", "2026.1"),
        )
