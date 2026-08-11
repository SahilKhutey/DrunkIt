# FACCP Privacy Architecture

## Privacy-by-Design Principles
1. **Data Minimization**: Only the `consumer-service` stores encrypted PII. Other services interact purely via `consumer_id` and zero-knowledge claim tokens.
2. **Pseudonymization**: Names and DOBs are pseudonymized with HMAC-SHA256 hashes for fast lookup without exposing plain values.
3. **GDPR Consent Engine**: Explicit tracking of purpose-based consent flags with revocation timestamp logs.
4. **Field Encryption**: AES-256 CBC (Fernet) field-level encryption for all sensitive identity records.
