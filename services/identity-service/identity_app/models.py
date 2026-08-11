from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    REGULATORY_ADMIN = "REGULATORY_ADMIN"
    RETAILER_ADMIN = "RETAILER_ADMIN"
    STORE_MANAGER = "STORE_MANAGER"
    INVENTORY_STAFF = "INVENTORY_STAFF"
    PACKER = "PACKER"
    DELIVERY_AGENT = "DELIVERY_AGENT"
    CONSUMER = "CONSUMER"

class VerificationLevel(str, Enum):
    C0_GUEST = "C0_GUEST"
    C1_REGISTERED = "C1_REGISTERED"
    C2_IDENTITY_VERIFIED = "C2_IDENTITY_VERIFIED"
    C3_AGE_ELIGIBLE = "C3_AGE_ELIGIBLE"
    C4_TRANSACTION_VERIFIED = "C4_TRANSACTION_VERIFIED"

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.CONSUMER
    jurisdiction: str = "IN-KA"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyAgeRequest(BaseModel):
    consumer_id: str
    dob_year: int
    government_id_ref: Optional[str] = None
    jurisdiction: str = "IN-KA"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    verification_level: VerificationLevel
    age_eligible: bool

class ZeroKnowledgeProofResponse(BaseModel):
    consumer_id: str
    identity_verified: bool
    age_eligible: bool
    jurisdiction: str
    verification_timestamp: str
    proof_token: str
