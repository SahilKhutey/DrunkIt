from pydantic import BaseModel, Field
from typing import Any


class AuditEventRecordRequest(BaseModel):

    event_type: str

    actor_type: str = "CONSUMER"

    actor_id: str | None = None

    subject_type: str | None = None

    subject_id: str | None = None

    service: str = "order-service"

    action: str = "CREATE_ORDER"

    outcome: str = "SUCCESS"

    correlation_id: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)


class PolicyCreateRequest(BaseModel):

    name: str

    jurisdiction: str = "IN-GJ"

    scope: str = "CONSUMER_VERIFICATION"

    rules: list[dict] = Field(default_factory=list)


class EvidenceCreateRequest(BaseModel):

    evidence_type: str

    subject_type: str

    subject_id: str

    source: str

    external_reference: str | None = None


class ConsentGrantRequest(BaseModel):

    subject_id: str

    consent_type: str

    version: str = "1.0"

    source: str = "MOBILE_APP"


class ApprovalCreateRequest(BaseModel):

    action: str

    resource_type: str

    resource_id: str

    risk_level: str = "HIGH"


class LegalHoldCreateRequest(BaseModel):

    name: str

    reason: str

    subject_id: str
