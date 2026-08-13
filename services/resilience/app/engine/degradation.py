class ResiliencePolicyEngine:

    def action_for(self, dependency: str, failure_type: str = "OUTAGE") -> str:
        dep = dependency.lower()
        if dep in ("compliance", "identity", "security", "verification"):
            return "FAIL_CLOSED"
        if dep == "payment":
            return "BLOCK_NEW_TRANSACTION"
        if dep in ("catalog", "catalogue"):
            return "READ_ONLY"
        if dep == "delivery":
            return "CONTROLLED_DEGRADED"
        return "DEGRADED"
