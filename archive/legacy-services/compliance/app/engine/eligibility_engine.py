from datetime import datetime, timezone


class EligibilityEngine:

    async def check_retailer_license(self, licenses: list, jurisdiction_id: str) -> str:
        if not licenses:
            return "DENY"

        now = datetime.now(timezone.utc)
        for lic in licenses:
            status = getattr(lic, "status", lic.get("status"))
            jur = getattr(lic, "jurisdiction_id", lic.get("jurisdiction_id"))
            until = getattr(lic, "valid_until", lic.get("valid_until"))

            if status != "VERIFIED":
                continue
            if jur != jurisdiction_id:
                continue
            if until and until < now:
                continue

            return "ALLOW"

        return "DENY"
