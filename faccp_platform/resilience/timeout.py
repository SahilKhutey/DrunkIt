"""Timeout execution wrapper."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


async def with_timeout(
    operation: Callable[[], Awaitable[T]],
    timeout_seconds: float,
) -> T:
    """Execute async operation with strict timeout constraint."""
    try:
        return await asyncio.wait_for(operation(), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation exceeded {timeout_seconds}s limit")
