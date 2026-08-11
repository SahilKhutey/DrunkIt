"""
Conflict-free Replicated Data Types (CRDTs) for multi-region consistency.

This module provides:
- GCounter: grow-only counter
- PNCounter: positive-negative counter
- ORSet: observed-remove set
- LWWRegister: last-writer-wins register
- MVRegister: multi-value register
"""

from __future__ import annotations

import threading
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


def get_node_id() -> str:
    """Return a stable node identifier for this instance."""
    import os
    return os.environ.get("FACCP_NODE_ID", f"node_{uuid.uuid4().hex[:12]}")


def monotonic_ts() -> int:
    """Monotonically increasing timestamp (in microseconds)."""
    return time.time_ns() // 1000


class CRDT(ABC, Generic[T]):
    """Base CRDT interface."""

    @abstractmethod
    def merge(self, other: "CRDT[T]") -> None:
        """Merge another replica's state into this one."""
        ...

    @abstractmethod
    def value(self) -> T:
        """Get the current value."""
        ...

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize for transmission."""
        ...

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> "CRDT[T]":
        """Deserialize from received data."""
        ...


class GCounter(CRDT[int]):
    """Grow-only counter."""

    def __init__(self, node_id: str | None = None) -> None:
        self._node_id = node_id or get_node_id()
        self._counters: dict[str, int] = {self._node_id: 0}
        self._lock = threading.Lock()

    def increment(self, delta: int = 1) -> None:
        with self._lock:
            self._counters[self._node_id] = self._counters.get(self._node_id, 0) + delta

    def value(self) -> int:
        with self._lock:
            return sum(self._counters.values())

    def merge(self, other: GCounter) -> None:
        with self._lock:
            for node, count in other._counters.items():
                self._counters[node] = max(self._counters.get(node, 0), count)

    def to_dict(self) -> dict[str, Any]:
        return {"type": "gcounter", "node_id": self._node_id, "counters": dict(self._counters)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GCounter:
        gc = cls(node_id=data["node_id"])
        gc._counters = dict(data["counters"])
        return gc


class PNCounter(CRDT[int]):
    """Positive-negative counter."""

    def __init__(self, node_id: str | None = None) -> None:
        self._node_id = node_id or get_node_id()
        self._positive = GCounter(self._node_id)
        self._negative = GCounter(self._node_id)

    def increment(self, delta: int = 1) -> None:
        if delta >= 0:
            self._positive.increment(delta)
        else:
            self._negative.increment(-delta)

    def decrement(self, delta: int = 1) -> None:
        self._negative.increment(delta)

    def value(self) -> int:
        return self._positive.value() - self._negative.value()

    def merge(self, other: PNCounter) -> None:
        self._positive.merge(other._positive)
        self._negative.merge(other._negative)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "pncounter",
            "node_id": self._node_id,
            "positive": self._positive.to_dict(),
            "negative": self._negative.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PNCounter:
        pn = cls(node_id=data["node_id"])
        pn._positive = GCounter.from_dict(data["positive"])
        pn._negative = GCounter.from_dict(data["negative"])
        return pn


class ORSet(CRDT[set]):
    """Observed-Remove Set."""

    def __init__(self, node_id: str | None = None) -> None:
        self._node_id = node_id or get_node_id()
        self._elements: dict[Any, set[str]] = {}
        self._tombstones: set[str] = set()
        self._lock = threading.Lock()

    def add(self, element: Any) -> None:
        with self._lock:
            tag = f"{self._node_id}:{monotonic_ts()}:{uuid.uuid4().hex[:8]}"
            self._elements.setdefault(element, set()).add(tag)

    def remove(self, element: Any) -> None:
        with self._lock:
            if element in self._elements:
                for tag in self._elements[element]:
                    self._tombstones.add(tag)
                del self._elements[element]

    def value(self) -> set:
        with self._lock:
            return {e for e, tags in self._elements.items() if tags - self._tombstones}

    def merge(self, other: ORSet) -> None:
        with self._lock:
            for element, tags in other._elements.items():
                self._elements.setdefault(element, set()).update(tags)
            self._tombstones.update(other._tombstones)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "orset",
            "node_id": self._node_id,
            "elements": {str(k): list(v) for k, v in self._elements.items()},
            "tombstones": list(self._tombstones),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ORSet:
        orset = cls(node_id=data["node_id"])
        orset._elements = {k: set(v) for k, v in data["elements"].items()}
        orset._tombstones = set(data["tombstones"])
        return orset


class LWWRegister(CRDT[Any]):
    """Last-Writer-Wins register."""

    def __init__(self, initial: Any = None, node_id: str | None = None) -> None:
        self._node_id = node_id or get_node_id()
        self._value: Any = initial
        self._ts: int = monotonic_ts() if initial is not None else 0
        self._lock = threading.Lock()

    def set(self, value: Any) -> None:
        with self._lock:
            self._value = value
            self._ts = monotonic_ts()

    def value(self) -> Any:
        with self._lock:
            return self._value

    def merge(self, other: LWWRegister) -> None:
        with self._lock:
            if other._ts > self._ts or (other._ts == self._ts and other._node_id > self._node_id):
                self._value = other._value
                self._ts = other._ts
                self._node_id = other._node_id

    def to_dict(self) -> dict[str, Any]:
        return {"type": "lww", "node_id": self._node_id, "value": self._value, "ts": self._ts}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LWWRegister:
        r = cls(node_id=data["node_id"])
        r._value = data["value"]
        r._ts = data["ts"]
        return r


class MVRegister(CRDT[list]):
    """Multi-Value Register: preserves concurrent writes."""

    def __init__(self, node_id: str | None = None) -> None:
        self._node_id = node_id or get_node_id()
        self._versions: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def set(self, value: Any) -> None:
        with self._lock:
            self._versions = [{"value": value, "ts": monotonic_ts(), "node_id": self._node_id}]

    def merge(self, other: MVRegister) -> None:
        with self._lock:
            all_versions = self._versions + other._versions
            by_node: dict[str, dict] = {}
            for v in all_versions:
                if v["node_id"] not in by_node or v["ts"] > by_node[v["node_id"]]["ts"]:
                    by_node[v["node_id"]] = v
            self._versions = list(by_node.values())

    def value(self) -> list:
        with self._lock:
            return [v["value"] for v in self._versions]

    def resolve(self, resolver: Any) -> Any:
        versions = self.value()
        if len(versions) == 1:
            return versions[0]
        return resolver(versions)

    def to_dict(self) -> dict[str, Any]:
        return {"type": "mv", "node_id": self._node_id, "versions": list(self._versions)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MVRegister:
        r = cls(node_id=data["node_id"])
        r._versions = list(data["versions"])
        return r
