"""
Shared test configuration.

Rate limiting is disabled for the whole test session: the suite fires
many requests in quick succession from what slowapi sees as a single
client, which would otherwise trip the same 429s a real abusive client
should hit. Rate limiting itself isn't what these tests are for — the
limiter's thresholds are simple enough to trust without a dedicated
test, and disabling it here keeps every other test deterministic.
"""
import os

os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
