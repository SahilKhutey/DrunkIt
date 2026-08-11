from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

class LicenseStatus(str, Enum):
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    VERIFIED = "VERIFIED"
    ACTIVE = "ACTIVE"
    EXPIRING = "EXPIRING"
    SUSPENDED = "SUSPENDED"

class SellerTrustLevel(str, Enum):
    S0_APPLICATION = "S0_APPLICATION"
    S1_BUSINESS_VERIFIED = "S1_BUSINESS_VERIFIED"
    S2_LICENSE_VERIFIED = "S2_LICENSE_VERIFIED"
    S3_STORE_VERIFIED = "S3_STORE_VERIFIED"
    S4_OPERATIONALLY_VERIFIED = "S4_OPERATIONALLY_VERIFIED"
    S5_FULLY_COMPLIANT = "S5_FULLY_COMPLIANT"

class ExciseLicenseRecord(BaseModel):
    license_id: str
    license_number: str
    license_type: str
    issuing_authority: str
    jurisdiction: str
    holder_name: str
    store_id: str
    valid_from: str
    valid_until: str
    permitted_categories: List[str]
    status: LicenseStatus

class StoreResponse(BaseModel):
    store_id: str
    organization_name: str
    name: str
    address: str
    city: str
    state: str
    jurisdiction: str
    pincode: str
    latitude: float
    longitude: float
    trust_level: SellerTrustLevel
    active: bool
    license: Optional[ExciseLicenseRecord] = None
