# FACCP Consumer Service

Consumer Profiles, Delivery Address Book, Age Verification Records, and Tier Progression.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /api/v1/consumer/profile | — | Create consumer profile |
| GET | /api/v1/consumer/profile/{consumer_id} | ✓ | Get profile details |
| POST | /api/v1/consumer/profile/{consumer_id}/addresses | ✓ | Add delivery address |
| GET | /api/v1/consumer/profile/{consumer_id}/addresses | ✓ | List delivery addresses |
| DELETE | /api/v1/consumer/profile/{consumer_id}/addresses/{address_id} | ✓ | Delete address |
| POST | /api/v1/consumer/profile/{consumer_id}/age-verification | ✓ | Submit age verification (upgrades to C2) |

## Consumer Tier Progression

1. **C0_ANONYMOUS**: Unregistered browsing.
2. **C1_REGISTERED**: Account registered (email/phone verified).
3. **C2_AGE_VERIFIED**: Age verification passed (Aadhaar / PAN / DL).
4. **C3_FULL_KYC**: Full KYC verified.

## Database

Schema in `alembic/versions/0001_initial.py`. Tables:

- `consumer_profiles` — Vault holding consumer profile & level status
- `delivery_addresses` — Geo-coded address book
- `age_verification_records` — Audit trail of document age verifications
- `consumer_preferences` — Notification & category preferences

## Development

```bash
# Run migrations
uv run alembic upgrade head

# Seed consumer profiles
uv run python -m app.scripts.seed_consumers

# Start service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```
