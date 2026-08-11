export enum SystemRole {
  PLATFORM_ROOT = 'PLATFORM_ROOT',
  SUPER_ADMIN = 'SUPER_ADMIN',
  REGULATORY_ADMIN = 'REGULATORY_ADMIN',
  STATE_ADMIN = 'STATE_ADMIN',
  DISTRICT_ADMIN = 'DISTRICT_ADMIN',
  CITY_ADMIN = 'CITY_ADMIN',
  COMPLIANCE_OFFICER = 'COMPLIANCE_OFFICER',
  ZONAL_LICENSING_OFFICER = 'ZONAL_LICENSING_OFFICER',
  NATIONAL_LICENSING_AUTHORITY = 'NATIONAL_LICENSING_AUTHORITY',
  EXCISE_INSPECTOR = 'EXCISE_INSPECTOR',
  SECURITY_ADMIN = 'SECURITY_ADMIN',
  FRAUD_INVESTIGATOR = 'FRAUD_INVESTIGATOR',
  INCIDENT_RESPONDER = 'INCIDENT_RESPONDER',
  SECURITY_ANALYST = 'SECURITY_ANALYST',
  DATA_PROTECTION_OFFICER = 'DATA_PROTECTION_OFFICER',
  FINANCE_ADMIN = 'FINANCE_ADMIN',
  SETTLEMENT_OFFICER = 'SETTLEMENT_OFFICER',
  RECONCILIATION_ANALYST = 'RECONCILIATION_ANALYST',
  TAX_OFFICER = 'TAX_OFFICER',
  SUPPORT_ADMIN = 'SUPPORT_ADMIN',
  TIER_1_AGENT = 'TIER_1_AGENT',
  TIER_2_AGENT = 'TIER_2_AGENT',
  ESCALATION_MANAGER = 'ESCALATION_MANAGER',
  INTERNAL_AUDITOR = 'INTERNAL_AUDITOR',
  EXTERNAL_AUDITOR = 'EXTERNAL_AUDITOR',

  // Retailer Domain
  RETAILER_OWNER = 'RETAILER_OWNER',
  ORG_ADMIN = 'ORG_ADMIN',
  REGIONAL_MANAGER = 'REGIONAL_MANAGER',
  STORE_MANAGER = 'STORE_MANAGER',
  INVENTORY_MANAGER = 'INVENTORY_MANAGER',
  INVENTORY_STAFF = 'INVENTORY_STAFF',
  STOCK_AUDITOR = 'STOCK_AUDITOR',
  PRICING_MANAGER = 'PRICING_MANAGER',
  ORDER_MANAGER = 'ORDER_MANAGER',
  PACKER = 'PACKER',
  DISPATCHER = 'DISPATCHER',
  STORE_ACCOUNTANT = 'STORE_ACCOUNTANT',
  FLEET_OWNER = 'FLEET_OWNER',
  FLEET_MANAGER = 'FLEET_MANAGER',
  DISPATCH_SUPERVISOR = 'DISPATCH_SUPERVISOR',
  DELIVERY_AGENT = 'DELIVERY_AGENT',
  SENIOR_AGENT = 'SENIOR_AGENT',
  JUNIOR_AGENT = 'JUNIOR_AGENT',
  FLEET_ACCOUNTANT = 'FLEET_ACCOUNTANT',

  // Consumer Domain
  GUEST = 'GUEST',
  REGISTERED = 'REGISTERED',
  IDENTITY_VERIFIED = 'IDENTITY_VERIFIED',
  AGE_ELIGIBLE = 'AGE_ELIGIBLE',
  TRANSACTION_VERIFIED = 'TRANSACTION_VERIFIED',
  BUSINESS_BUYER = 'BUSINESS_BUYER',
  TRUSTED_BUYER = 'TRUSTED_BUYER'
}

export enum PermissionAction {
  CREATE = 'CREATE',
  READ = 'READ',
  UPDATE = 'UPDATE',
  DELETE = 'DELETE',
  VERIFY = 'VERIFY',
  APPROVE = 'APPROVE',
  EXECUTE = 'EXECUTE',
  EXPORT = 'EXPORT'
}

export enum PrivacyClassification {
  P0_PUBLIC = 'P0_PUBLIC',
  P1_ACCOUNT = 'P1_ACCOUNT',
  P2_TRANSACTION = 'P2_TRANSACTION',
  P3_IDENTITY_KYC = 'P3_IDENTITY_KYC'
}

export enum BreakGlassLevel {
  NONE = 'NONE',
  LEVEL_1_FRAUD = 'LEVEL_1_FRAUD',
  LEVEL_2_REGULATORY = 'LEVEL_2_REGULATORY',
  LEVEL_3_SYSTEM_ROOT = 'LEVEL_3_SYSTEM_ROOT'
}

export interface SubjectAttributes {
  userId: string;
  role: SystemRole;
  organizationId?: string;
  assignedStores: string[];
  assignedJurisdictions: string[];
  mfaLevel: 'NONE' | 'SMS' | 'TOTP' | 'HARDWARE_KEY' | 'BIOMETRIC';
  deviceTrustScore: number;
  riskScore: number;
  breakGlassLevel: BreakGlassLevel;
}

export interface ResourceAttributes {
  resourceId: string;
  resourceType: string;
  resourceOwnerId?: string;
  jurisdiction: string;
  classification: PrivacyClassification;
  licenseStatus?: string;
  storeId?: string;
  requiresLicense?: boolean;
}

export interface EnvironmentAttributes {
  timestampIso: string;
  clientIp: string;
  geoLocation?: { latitude: number; longitude: number };
  geoJurisdiction: string;
  networkZone: 'PUBLIC' | 'PRIVATE' | 'MGMT';
  vpnDetected: boolean;
  mfaFreshnessSeconds: number;
}

export interface PolicyEvaluationResult {
  decision: 'ALLOW' | 'DENY' | 'CHALLENGE' | 'SOD_VIOLATION';
  ruleId?: string;
  reason: string;
  requiresStepUpMfa: boolean;
  evaluatedAtIso: string;
}
