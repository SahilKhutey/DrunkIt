from pydantic import BaseModel


class ComplianceDecision(BaseModel):

    allowed: bool

    decision_code: str

    verification_required: bool

    verification_stage: str | None = None

    reason: str | None = None
