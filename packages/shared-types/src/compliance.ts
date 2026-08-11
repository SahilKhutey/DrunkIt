export enum DecisionResult {
  ALLOW = 'ALLOW',
  DENY = 'DENY',
  ADDITIONAL_VERIFICATION_REQUIRED = 'ADDITIONAL_VERIFICATION_REQUIRED'
}

export interface ComplianceEvaluationRequest {
  consumerId: string;
  storeId: string;
  jurisdiction: string;
  orderTimestamp: string;
  items: Array<{
    category: string;
    abv: number;
    quantity: number;
    volumeMl: number;
  }>;
}

export interface ComplianceDecision {
  decisionId: string;
  result: DecisionResult;
  jurisdiction: string;
  policyVersion: string;
  reasons: string[];
  evaluatedAt: string;
}
