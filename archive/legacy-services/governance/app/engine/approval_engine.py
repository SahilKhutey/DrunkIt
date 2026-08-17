from datetime import datetime, timezone
from uuid import uuid4


class ApprovalEngine:

    def __init__(self):
        self.requests: dict[str, dict] = {}

    async def create_request(
        self,
        actor: str,
        action: str,
        resource_type: str,
        resource_id: str,
        risk_level: str = "HIGH",
    ) -> dict:

        required = {"LOW": 1, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 2}.get(risk_level, 1)

        req_id = str(uuid4())
        req = {
            "id": req_id,
            "action": action,
            "requested_by": actor,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "risk_level": risk_level,
            "status": "PENDING",
            "required_approvals": required,
            "approvals": [],
            "created_at": datetime.now(timezone.utc),
        }
        self.requests[req_id] = req
        return req

    async def approve(self, request_id: str, approver: str) -> dict:
        req = self.requests.get(request_id)
        if not req:
            raise ValueError("APPROVAL_REQUEST_NOT_FOUND")

        # Separation of Duties check
        if req["requested_by"] == approver:
            raise PermissionError("SELF_APPROVAL_FORBIDDEN")

        if approver not in req["approvals"]:
            req["approvals"].append(approver)

        if len(req["approvals"]) >= req["required_approvals"]:
            req["status"] = "APPROVED"

        return req
