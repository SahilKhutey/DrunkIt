"""HTTP Risk Engine client."""

from __future__ import annotations

import httpx


class RiskClient:
    """HTTP client communicating with Risk Service API boundary."""

    def __init__(self, base_url: str = "http://localhost:8012") -> None:
        self.base_url = base_url.rstrip("/")

    async def evaluate(self, payload: dict) -> dict:
        """Post risk evaluation request to Risk Service."""
        url = f"{self.base_url}/risk/evaluate"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
