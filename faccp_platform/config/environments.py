"""Environment definitions for FACCP Platform."""

from __future__ import annotations

from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"
