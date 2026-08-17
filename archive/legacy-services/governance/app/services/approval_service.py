from services.governance.app.engine.approval_engine import ApprovalEngine


class ApprovalService:

    def __init__(self, approval_engine: ApprovalEngine | None = None):
        self.approval_engine = approval_engine or ApprovalEngine()

    async def create_request(
        self,
        actor: str,
        action: str,
        resource_type: str,
        resource_id: str,
        risk_level: str = "HIGH",
    ) -> dict:

        return await self.approval_engine.create_request(actor, action, resource_type, resource_id, risk_level)

    async def approve_request(self, request_id: str, approver: str) -> dict:
        return await self.approval_engine.approve(request_id, approver)
