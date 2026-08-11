from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

class DecisionResult(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    ADDITIONAL_VERIFICATION_REQUIRED = "ADDITIONAL_VERIFICATION_REQUIRED"

class OrderItemCompliance(BaseModel):
    category: str
    abv: float
    quantity: int
    volume_ml: int

class ComplianceEvaluationRequest(BaseModel):
    consumer_id: str
    consumer_age_eligible: bool
    store_id: str
    jurisdiction: str
    license_status: str
    order_timestamp_iso: str
    items: List[OrderItemCompliance]

class ComplianceDecisionResponse(BaseModel):
    decision_id: str
    result: DecisionResult
    jurisdiction: str
    policy_version: str
    reasons: List[str]
    evaluated_at: str
