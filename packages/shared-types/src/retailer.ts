export enum SellerTrustLevel {
  S0_APPLICATION = 'S0_APPLICATION',
  S1_BUSINESS_VERIFIED = 'S1_BUSINESS_VERIFIED',
  S2_LICENSE_VERIFIED = 'S2_LICENSE_VERIFIED',
  S3_STORE_VERIFIED = 'S3_STORE_VERIFIED',
  S4_OPERATIONALLY_VERIFIED = 'S4_OPERATIONALLY_VERIFIED',
  S5_FULLY_COMPLIANT = 'S5_FULLY_COMPLIANT'
}

export enum LicenseStatus {
  PENDING = 'PENDING',
  UNDER_REVIEW = 'UNDER_REVIEW',
  VERIFIED = 'VERIFIED',
  ACTIVE = 'ACTIVE',
  EXPIRING = 'EXPIRING',
  SUSPENDED = 'SUSPENDED',
  EXPIRED = 'EXPIRED',
  REVOKED = 'REVOKED'
}

export enum StaffRole {
  RETAILER_ADMIN = 'RETAILER_ADMIN',
  STORE_MANAGER = 'STORE_MANAGER',
  INVENTORY_MANAGER = 'INVENTORY_MANAGER',
  PACKER = 'PACKER',
  AUTHORIZED_SALES_STAFF = 'AUTHORIZED_SALES_STAFF'
}

export interface ExciseLicense {
  licenseId: string;
  licenseNumber: string;
  licenseType: string;
  issuingAuthority: string;
  jurisdiction: string;
  holderName: string;
  storeId: string;
  validFrom: string;
  validUntil: string;
  permittedCategories: string[];
  status: LicenseStatus;
}

export interface StoreLocation {
  storeId: string;
  organizationId: string;
  name: string;
  address: string;
  city: string;
  state: string;
  pincode: string;
  latitude: number;
  longitude: number;
  trustLevel: SellerTrustLevel;
  active: boolean;
}
