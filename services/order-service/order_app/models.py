from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

class OrderStatus(str, Enum):
    CREATED = "CREATED"
    VALIDATING = "VALIDATING"
    COMPLIANCE_CHECK = "COMPLIANCE_CHECK"
    CONFIRMED = "CONFIRMED"
    RETAILER_ACCEPTED = "RETAILER_ACCEPTED"
    PICKING = "PICKING"
    PACKED = "PACKED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERY_VERIFICATION = "DELIVERY_VERIFICATION"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    COMPLIANCE_BLOCKED = "COMPLIANCE_BLOCKED"

class CreateOrderItem(BaseModel):
    sku: str
    product_name: str
    category: str
    abv: float
    volume_ml: int
    quantity: int
    unit_price: float

class CreateOrderRequest(BaseModel):
    consumer_id: str
    consumer_age_eligible: bool
    store_id: str
    jurisdiction: str
    items: List[CreateOrderItem]

class OrderResponse(BaseModel):
    order_id: str
    consumer_id: str
    store_id: str
    jurisdiction: str
    items: List[CreateOrderItem]
    subtotal: float
    tax: float
    delivery_fee: float
    platform_fee: float
    total_amount: float
    status: OrderStatus
    compliance_decision_id: Optional[str] = None
    delivery_otp: Optional[str] = None
    reasons: List[str] = []
    created_at: str
