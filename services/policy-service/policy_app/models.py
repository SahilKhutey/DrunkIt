from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SystemRole(str, Enum):
    PLATFORM_ROOT = "PLATFORM_ROOT"
    SUPER_ADMIN = "SUPER_ADMIN"
    REGULATORY_ADMIN = "REGULATORY_ADMIN"
    STATE_ADMIN = "STATE_ADMIN"
    DISTRICT_ADMIN = "DISTRICT_ADMIN"
    CITY_ADMIN = "CITY_ADMIN"
    COMPLIANCE_OFFICER = "COMPLIANCE_OFFICER"
    ZONAL_LICENSING_OFFICER = "ZONAL_LICENSING_OFFICER"
    NATIONAL_LICENSING_AUTHORITY = "NATIONAL_LICENSING_AUTHORITY"
    EXCISE_INSPECTOR = "EXCISE_INSPECTOR"
    SECURITY_ADMIN = "SECURITY_ADMIN"
    FRAUD_INVESTIGATOR = "FRAUD_INVESTIGATOR"
    INCIDENT_RESPONDER = "INCIDENT_RESPONDER"
    SECURITY_ANALYST = "SECURITY_ANALYST"
    DATA_PROTECTION_OFFICER = "DATA_PROTECTION_OFFICER"
    FINANCE_ADMIN = "FINANCE_ADMIN"
    SETTLEMENT_OFFICER = "SETTLEMENT_OFFICER"
    RECONCILIATION_ANALYST = "RECONCILIATION_ANALYST"
    TAX_OFFICER = "TAX_OFFICER"
    SUPPORT_ADMIN = "SUPPORT_ADMIN"
    TIER_1_AGENT = "TIER_1_AGENT"
    TIER_2_AGENT = "TIER_2_AGENT"
    ESCALATION_MANAGER = "ESCALATION_MANAGER"
    INTERNAL_AUDITOR = "INTERNAL_AUDITOR"
    EXTERNAL_AUDITOR = "EXTERNAL_AUDITOR"

    # Retailer Domain
    RETAILER_OWNER = "RETAILER_OWNER"
    ORG_ADMIN = "ORG_ADMIN"
    REGIONAL_MANAGER = "REGIONAL_MANAGER"
    STORE_MANAGER = "STORE_MANAGER"
    INVENTORY_MANAGER = "INVENTORY_MANAGER"
    INVENTORY_STAFF = "INVENTORY_STAFF"
    STOCK_AUDITOR = "STOCK_AUDITOR"
    PRICING_MANAGER = "PRICING_MANAGER"
    ORDER_MANAGER = "ORDER_MANAGER"
    PACKER = "PACKER"
    DISPATCHER = "DISPATCHER"
    STORE_ACCOUNTANT = "STORE_ACCOUNTANT"
    FLEET_OWNER = "FLEET_OWNER"
    FLEET_MANAGER = "FLEET_MANAGER"
    DISPATCH_SUPERVISOR = "DISPATCH_SUPERVISOR"
    DELIVERY_AGENT = "DELIVERY_AGENT"
    SENIOR_AGENT = "SENIOR_AGENT"
    JUNIOR_AGENT = "JUNIOR_AGENT"
    FLEET_ACCOUNTANT = "FLEET_ACCOUNTANT"

    # Consumer Domain
    GUEST = "GUEST"
    REGISTERED = "REGISTERED"
    IDENTITY_VERIFIED = "IDENTITY_VERIFIED"
    AGE_ELIGIBLE = "AGE_ELIGIBLE"
    TRANSACTION_VERIFIED = "TRANSACTION_VERIFIED"
    BUSINESS_BUYER = "BUSINESS_BUYER"
    TRUSTED_BUYER = "TRUSTED_BUYER"

class PermissionAction(str, Enum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    VERIFY = "VERIFY"
    APPROVE = "APPROVE"
    EXECUTE = "EXECUTE"
    EXPORT = "EXPORT"

class PrivacyClassification(str, Enum):
    P0_PUBLIC = "P0_PUBLIC"
    P1_ACCOUNT = "P1_ACCOUNT"
    P2_TRANSACTION = "P2_TRANSACTION"
    P3_IDENTITY_KYC = "P3_IDENTITY_KYC"

class BreakGlassLevel(str, Enum):
    NONE = "NONE"
    LEVEL_1_FRAUD = "LEVEL_1_FRAUD"
    LEVEL_2_REGULATORY = "LEVEL_2_REGULATORY"
    LEVEL_3_SYSTEM_ROOT = "LEVEL_3_SYSTEM_ROOT"

class SubjectAttributes(BaseModel):
    user_id: str
    role: SystemRole
    organization_id: Optional[str] = None
    assigned_stores: List[str] = Field(default_factory=list)
    assigned_jurisdictions: List[str] = Field(default_factory=list)
    mfa_level: str = "TOTP"
    device_trust_score: int = 80
    risk_score: int = 10
    break_glass_level: BreakGlassLevel = BreakGlassLevel.NONE

class ResourceAttributes(BaseModel):
    resource_id: str
    resource_type: str
    resource_owner_id: Optional[str] = None
    jurisdiction: str
    classification: PrivacyClassification = PrivacyClassification.P0_PUBLIC
    license_status: Optional[str] = "ACTIVE"
    store_id: Optional[str] = None
    requires_license: bool = False

class EnvironmentAttributes(BaseModel):
    timestamp_iso: str
    client_ip: str
    geo_jurisdiction: str
    network_zone: str = "PUBLIC"
    vpn_detected: bool = False
    mfa_freshness_seconds: int = 300

class EvaluatePolicyRequest(BaseModel):
    subject: SubjectAttributes
    action: PermissionAction
    resource: ResourceAttributes
    environment: EnvironmentAttributes

class EvaluatePolicyResponse(BaseModel):
    decision: str  # ALLOW, DENY, CHALLENGE, SOD_VIOLATION
    rule_id: Optional[str] = None
    reason: str
    requires_step_up_mfa: bool = False
    evaluated_at_iso: str
