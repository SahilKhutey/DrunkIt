from typing import Any
from services.compliance.app.policies.base import CompliancePolicy


class IndiaJurisdictionPolicy(CompliancePolicy):

    policy_version = "india-policy-1"

    async def evaluate(
        self,
        context: Any,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError("Jurisdiction rules must be verified per legal authority before evaluation.")
