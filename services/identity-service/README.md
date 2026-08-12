# FACCP Identity Service

Authentication, MFA, sessions, and identity vault.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /api/v1/auth/register | — | Register a new user |
| POST | /api/v1/auth/login | — | Login (returns MFA challenge if enabled) |
| POST | /api/v1/auth/refresh | — | Refresh access token (with rotation) |
| POST | /api/v1/auth/logout | ✓ | Logout (current device or all) |
| GET | /api/v1/auth/me | ✓ | Current user profile |
| POST | /api/v1/auth/password/change | ✓ | Change password (revokes other sessions) |
| POST | /api/v1/auth/password/reset/request | — | Request password reset email |
| POST | /api/v1/auth/password/reset/confirm | — | Confirm reset with token |
| POST | /api/v1/auth/mfa/setup | ✓ | Begin TOTP MFA enrollment |
| POST | /api/v1/auth/mfa/verify | ✓ | Verify TOTP code, enable MFA |
| POST | /api/v1/auth/mfa/disable | ✓ | Disable MFA (requires current password) |
| GET | /api/v1/auth/sessions | ✓ | List active sessions |

## Security Features

- **Argon2id** password hashing (memory=64MB, time=3, parallelism=4)
- **JWT access tokens** (15 min lifetime, RS256 ready)
- **Refresh token rotation** with family-based reuse detection
- **TOTP MFA** with backup codes
- **Field-level encryption** for MFA secrets
- **Account lockout** after 5 failed attempts
- **Session limit** (5 concurrent sessions)
- **Absolute timeout** (8 hours) + idle timeout (30 min)
- **Audit events** for all sensitive actions

## Database

Schema in `alembic/versions/0001_initial.py`. Tables:

- `users` — Core identity (email, phone, roles, MFA, trust/risk)
- `sessions` — Server-side sessions with timeouts
- `devices` — Registered device fingerprints with trust scores
- `api_keys` — Service-to-service API keys
- `role_definitions` — Persisted role/permission definitions
- `password_reset_tokens` — Short-lived reset tokens
- `email_verification_tokens` — Email verification tokens

## Development

```bash
# Run migrations
uv run alembic upgrade head

# Seed roles and permissions
uv run python -m app.scripts.seed_rbac

# Start service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```
