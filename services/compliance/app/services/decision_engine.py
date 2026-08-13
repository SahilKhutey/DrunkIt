class DecisionEngine:

    async def decide(
        self,
        checks: list[dict],
    ) -> dict:

        reasons = []
        actions = []

        for check in checks:

            if check.get("status") == "DENY":
                reasons.append(check.get("reason", "Unknown policy violation"))

            elif check.get("status") == "HOLD":
                actions.append(check.get("action", "VERIFICATION_REQUIRED"))

        if reasons:
            return {
                "decision": "DENY",
                "reasons": reasons,
                "required_actions": [],
                "policy_version": "2026.1",
            }

        if actions:
            return {
                "decision": "HOLD",
                "reasons": [],
                "required_actions": actions,
                "policy_version": "2026.1",
            }

        return {
            "decision": "ALLOW",
            "reasons": [],
            "required_actions": [],
            "policy_version": "2026.1",
        }
