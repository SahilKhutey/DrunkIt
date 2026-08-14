"""Lifecycle hooks runner for platform applications."""

from __future__ import annotations

from typing import Callable


async def run_lifecycle_hooks(hooks: list[Callable]) -> None:
    """Execute a list of synchronous or asynchronous lifecycle hooks."""
    for hook in hooks:
        result = hook()
        if hasattr(result, "__await__"):
            await result
