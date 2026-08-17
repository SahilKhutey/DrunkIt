from datetime import datetime, timezone
from uuid import uuid4


class CaseService:

    def __init__(self):
        self.cases: dict[str, dict] = {}

    async def create_case(
        self,
        subject_type: str,
        subject_id: str,
        category: str = "ACCOUNT_TAKEOVER",
        priority: str = "HIGH",
    ) -> dict:

        case_id = str(uuid4())
        c = {
            "id": case_id,
            "subject_type": subject_type,
            "subject_id": subject_id,
            "category": category,
            "priority": priority,
            "status": "OPEN",
            "assigned_to": None,
            "created_at": datetime.now(timezone.utc),
        }
        self.cases[case_id] = c
        return c

    async def get_case(self, case_id: str) -> dict | None:
        return self.cases.get(case_id)

    async def list_cases(self, status: str | None = None) -> list[dict]:
        res = list(self.cases.values())
        if status:
            res = [c for c in res if c["status"] == status]
        return res
