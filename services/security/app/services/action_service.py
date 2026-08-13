from datetime import datetime, timezone
from uuid import uuid4


class ActionService:

    def __init__(self):
        self.actions: dict[str, dict] = {}

    async def execute_action(
        self,
        action: str,
        subject_type: str,
        subject_id: str,
        reason: str = "SECURITY_RULE_TRIGGERED",
    ) -> dict:

        act_id = str(uuid4())
        record = {
            "id": act_id,
            "subject_type": subject_type,
            "subject_id": subject_id,
            "action": action,
            "reason": reason,
            "expires_at": None,
            "created_at": datetime.now(timezone.utc),
        }
        self.actions[act_id] = record
        return record
