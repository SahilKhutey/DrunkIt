from pydantic import BaseModel


class RiskEvaluationRequest(BaseModel):

    subject_type: str

    subject_id: str

    operation: str = "GENERAL"

    order_id: str | None = None

    device_id: str | None = None

    session_id: str | None = None


class SecurityCaseCreateRequest(BaseModel):

    subject_type: str

    subject_id: str

    category: str = "ACCOUNT_TAKEOVER"

    priority: str = "HIGH"


class SecurityActionExecuteRequest(BaseModel):

    action: str

    subject_type: str

    subject_id: str

    reason: str = "SECURITY_RULE_TRIGGERED"


class SessionRevokeRequest(BaseModel):

    session_id: str
