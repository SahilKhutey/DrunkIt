"""
Unit-test suite configuration.

Rate limiting is disabled for the whole test session: the suite fires
many requests in quick succession from what slowapi sees as a single
client, which would otherwise trip the same 429s a real abusive client
should hit. Rate limiting itself isn't what these tests are for — the
limiter's thresholds are simple enough to trust without a dedicated
test, and disabling it here keeps every other test deterministic.

Legacy service imports (services.compliance, services.payment, etc.) are
bridged via the root conftest.py pytest_configure hook — no action needed here.

TODO (P1): As legacy service tests are rewritten to import from the canonical
           registered services (services/compliance-service/, etc.), this note
           and the root conftest bridge can be removed.
"""
import os

os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
