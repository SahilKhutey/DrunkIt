"""
Central configuration for the DrunkIt/FACCP MVP.

Every jurisdiction-sensitive value (legal drinking age per state, which
states are serviceable at all) lives in config/policy data, never
hardcoded inside business logic. This is what lets the Eligibility
Engine be reconfigured per state without a code change.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "DrunkIt FACCP MVP"
    environment: str = os.getenv("ENVIRONMENT", "development")

    # Local dev defaults to SQLite so the whole stack runs with zero
    # external infra. Point DATABASE_URL at Postgres for anything real.
    database_url: str = os.getenv(
        "DATABASE_URL", "sqlite:///./drunkit_mvp.db"
    )

    # Secret used to sign short-lived eligibility verification tokens.
    # MUST be overridden via env var in any non-local environment.
    eligibility_token_secret: str = os.getenv(
        "ELIGIBILITY_TOKEN_SECRET", "dev-only-insecure-secret-change-me"
    )
    eligibility_token_ttl_seconds: int = 15 * 60  # 15 minutes

    # Default delivery ETA window shown when no live estimate exists.
    default_eta_min_minutes: int = 25
    default_eta_max_minutes: int = 45

    # Master switch: if a state isn't in policies/jurisdictions.json
    # with allow_delivery=true, the platform refuses to serve it,
    # regardless of anything else in the request. Fail closed.
    fail_closed_on_missing_jurisdiction: bool = True

    # IP-based rate limiting. Set false in test environments (handled
    # via conftest.py) and can be disabled in local dev if needed.
    rate_limit_enabled: bool = bool(os.getenv("RATE_LIMIT_ENABLED", "true").lower() not in ("false", "0", "no"))

    # In dev/SQLite mode, allow create_all() as a shortcut instead of
    # running Alembic. Set to "false" when using Alembic migrations
    # (the Dockerfile CMD is the authoritative migration path).
    auto_create_tables: bool = bool(os.getenv("AUTO_CREATE_TABLES", "true").lower() not in ("false", "0", "no"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
