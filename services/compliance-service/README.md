# FACCP Compliance Service

Policy Engine, Jurisdiction Rules, Dry-Day Calendar, and Regulatory Compliance Evaluator.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /api/v1/compliance/policies | Admin | Create a new regulatory policy |
| GET | /api/v1/compliance/policies | — | List policies (optional jurisdiction filter) |
| GET | /api/v1/compliance/policies/{code} | — | Get policy by code |
| POST | /api/v1/compliance/dry-days | Admin | Record a dry day |
| GET | /api/v1/compliance/dry-days/check | — | Check if date is a dry day |
| POST | /api/v1/compliance/evaluate | — | Evaluate a transaction for compliance |

## Evaluation Engine Rules

1. **Purchasing Age Gate**: Validates consumer age against jurisdiction minimum (e.g. KA=21, MH=25).
2. **Transaction Volume Limit**: Enforces maximum volume per order (e.g. 4.5L).
3. **Sales Hours Gate**: Restricts purchases outside state excise operating hours (e.g. 10:00 AM - 10:00 PM).
4. **Dry Day Gate**: Prohibits transactions on national/state dry days (Republic Day, Independence Day, Gandhi Jayanti).
5. **Store License Gate**: Requires ACTIVE non-expired store excise license.
6. **Fail-Closed Resilience**: Fail-closed stance if no policy is registered for jurisdiction.

## Database

Schema in `alembic/versions/0001_initial.py`. Tables:

- `policies` — Regulatory policy definitions
- `jurisdiction_rules` — Specific rules under a policy
- `dry_day_calendars` — Dry day dates per state
- `license_requirements` — Store licensing requirements
- `compliance_checks` — Audit trail of evaluations

## Development

```bash
# Run migrations
uv run alembic upgrade head

# Seed policies and dry days
uv run python -m app.scripts.seed_policies

# Start service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8007 --reload
```
