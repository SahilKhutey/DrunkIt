"""
Feature Flag System as codified in Protocol 12 (§12.4).
Supports percentage rollouts, user allowlists, tenant allowlists, and deterministic hashing.
"""

from __future__ import annotations

import hashlib
from typing import Any


class FeatureFlag:
    def __init__(
        self,
        name: str,
        default: bool = False,
        rollout_percentage: int = 0,
        allowed_user_ids: list[str] | None = None,
        allowed_tenants: list[str] | None = None,
    ) -> None:
        self.name = name
        self.default = default
        self.rollout_percentage = max(0, min(100, rollout_percentage))
        self.allowed_user_ids: list[str] = allowed_user_ids or []
        self.allowed_tenants: list[str] = allowed_tenants or []


class FeatureFlagRegistry:
    _flags: dict[str, FeatureFlag] = {}

    @classmethod
    def register(cls, flag: FeatureFlag) -> None:
        cls._flags[flag.name] = flag

    @classmethod
    def get(cls, name: str) -> FeatureFlag | None:
        return cls._flags.get(name)

    @classmethod
    def clear(cls) -> None:
        cls._flags.clear()


async def is_enabled(flag_name: str, context: dict[str, Any] | None = None) -> bool:
    """Evaluate whether a feature flag is active for a given context."""
    flag = FeatureFlagRegistry.get(flag_name)
    if not flag:
        return False

    context = context or {}

    # 1. User allowlist check
    if "user_id" in context and context["user_id"] in flag.allowed_user_ids:
        return True

    # 2. Tenant allowlist check
    if "tenant_id" in context and context["tenant_id"] in flag.allowed_tenants:
        return True

    # 3. 100% or 0% rollout boundary
    if flag.rollout_percentage >= 100:
        return True
    if flag.rollout_percentage <= 0:
        return flag.default

    # 4. Deterministic MD5 hash rollout for percentage
    if "user_id" in context and context["user_id"]:
        user_hash = int(hashlib.md5(context["user_id"].encode("utf-8")).hexdigest(), 16)
        return (user_hash % 100) < flag.rollout_percentage

    return flag.default
