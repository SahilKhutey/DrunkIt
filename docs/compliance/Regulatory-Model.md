# FACCP Regulatory & Compliance Model

## Overview
FACCP enforces strict compliance for regulated alcohol distribution across varying state and federal jurisdictions.

## Verification Levels
- **C0_GUEST**: Unauthenticated visitor.
- **C1_REGISTERED**: Phone/email verified.
- **C2_IDENTITY_VERIFIED**: KYC document verified (Aadhaar / Passport / DL).
- **C3_AGE_ELIGIBLE**: Zero-Knowledge age proof valid for target jurisdiction state (18/21/25).
- **C4_TRANSACTION_VERIFIED**: Historical purchase verification complete.

## Statutory Rules Evaluated per Order
1. **Age Eligibility**: Verified against state-specific minimum drinking age laws (e.g. Karnataka: 21, Maharashtra: 25, Goa: 18).
2. **Dry Days**: Order timestamp checked against state excise dry day calendars.
3. **Sales Hours**: Order timestamp checked against state-permitted retail hours (e.g. 10:00–22:00).
4. **License Validity**: Retailer license checked for active status, non-expiration, and permitted category.
5. **Quantity Limits**: Order volume checked against state daily/per-transaction bulk limits.
6. **Delivery Zone**: Customer address verified within licensed retail delivery zones.
