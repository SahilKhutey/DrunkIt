"""Single source of truth for 'current time' across the app.

datetime.utcnow() is deprecated as of Python 3.12 because it returns a
naive datetime via a deprecated code path. This wrapper produces the
same naive-but-UTC value (matching the naive DateTime columns used
throughout the models) via a non-deprecated call. If this app moves to
timezone-aware columns later (recommended for Postgres), update this
in one place and the DB column types together.
"""
from __future__ import annotations

from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
