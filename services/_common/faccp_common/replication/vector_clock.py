"""
Vector clocks for tracking causality in distributed systems.
"""

from __future__ import annotations

import threading
from typing import Any


class VectorClock:

    def __init__(self, node_id: str, initial: dict[str, int] | None = None) -> None:
        self.node_id = node_id
        self.clock: dict[str, int] = initial or {node_id: 0}
        self._lock = threading.Lock()

    def tick(self) -> None:
        with self._lock:
            self.clock[self.node_id] = self.clock.get(self.node_id, 0) + 1

    def observe(self, other: VectorClock) -> None:
        with self._lock:
            for node, count in other.clock.items():
                self.clock[node] = max(self.clock.get(node, 0), count)
            self.clock[self.node_id] = self.clock.get(self.node_id, 0) + 1

    def merge(self, other: VectorClock) -> VectorClock:
        result = {**self.clock}
        for node, count in other.clock.items():
            result[node] = max(result.get(node, 0), count)
        return VectorClock(self.node_id, result)

    def dominates(self, other: VectorClock) -> bool:
        any_strict = False
        for node, count in self.clock.items():
            other_count = other.clock.get(node, 0)
            if count < other_count:
                return False
            if count > other_count:
                any_strict = True
        for node, count in other.clock.items():
            if node not in self.clock:
                return False
        return any_strict

    def concurrent_with(self, other: VectorClock) -> bool:
        return not self.dominates(other) and not other.dominates(self) and self != other

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, VectorClock):
            return False
        return self.clock == other.clock

    def __repr__(self) -> str:
        items = ", ".join(f"{k}:{v}" for k, v in sorted(self.clock.items()))
        return f"VC({items})"

    def to_dict(self) -> dict[str, int]:
        return dict(self.clock)

    @classmethod
    def from_dict(cls, data: dict[str, int], node_id: str) -> VectorClock:
        return cls(node_id=node_id, initial=dict(data))
