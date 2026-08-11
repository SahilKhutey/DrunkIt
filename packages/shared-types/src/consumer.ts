export enum VerificationLevel {
  C0_GUEST = 'C0_GUEST',
  C1_REGISTERED = 'C1_REGISTERED',
  C2_IDENTITY_VERIFIED = 'C2_IDENTITY_VERIFIED',
  C3_AGE_ELIGIBLE = 'C3_AGE_ELIGIBLE',
  C4_TRANSACTION_VERIFIED = 'C4_TRANSACTION_VERIFIED'
}

export interface ConsumerProfile {
  id: string;
  verificationLevel: VerificationLevel;
  ageEligible: boolean;
  jurisdiction: string;
  mfaEnabled: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ZeroKnowledgeAgeProof {
  consumerId: string;
  identityVerified: boolean;
  ageEligible: boolean;
  jurisdiction: string;
  verificationTimestamp: string;
  verificationProvider: string;
  signature: string;
}
