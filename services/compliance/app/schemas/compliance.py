from pydantic import BaseModel, Field


class ComplianceContext(BaseModel):

    consumer_id: str

    retailer_id: str

    jurisdiction: str

    product_category: str

    product_id: str

    quantity: int = Field(default=1, ge=1)

    delivery_latitude: float

    delivery_longitude: float

    order_value: float = Field(default=0.0, ge=0.0)


class ComplianceDecision(BaseModel):

    decision: str  # ALLOW, DENY, HOLD, REVIEW

    reasons: list[str] = Field(default_factory=list)

    required_actions: list[str] = Field(default_factory=list)

    policy_version: str = "2026.1"
