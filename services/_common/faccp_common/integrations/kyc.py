"""KYC (Know Your Customer) integration adapters."""

from __future__ import annotations

import hashlib
import secrets
from abc import abstractmethod
from datetime import datetime, timezone
from typing import Any

import httpx

from faccp_common.integrations.base import IntegrationAdapter, IntegrationConfig
from faccp_common.logging import get_logger

logger = get_logger(__name__)


class KYCAdapter(IntegrationAdapter):

    @abstractmethod
    async def create_check(
        self, user_id: str, user_info: dict[str, Any]
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    async def get_check_status(self, check_id: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def verify_age(self, user_id: str, document_data: dict[str, Any]) -> dict[str, Any]:
        ...


class StubKYCAdapter(KYCAdapter):

    def __init__(self, config: IntegrationConfig | None = None) -> None:
        super().__init__(config or IntegrationConfig(name="stub_kyc"))
        self._checks: dict[str, dict[str, Any]] = {}

    async def health_check(self) -> bool:
        return True

    async def create_check(self, user_id: str, user_info: dict[str, Any]) -> dict[str, Any]:
        check_id = f"kyc_{secrets.token_hex(12)}"
        self._checks[check_id] = {
            "check_id": check_id, "user_id": user_id,
            "status": "pending", "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return {"check_id": check_id, "status": "pending", "redirect_url": None}

    async def get_check_status(self, check_id: str) -> dict[str, Any]:
        check = self._checks.get(check_id, {})
        return check or {"check_id": check_id, "status": "not_found"}

    async def verify_age(self, user_id: str, document_data: dict[str, Any]) -> dict[str, Any]:
        dob = document_data.get("date_of_birth")
        if not dob:
            return {"age_eligible": False, "confidence": 0.0, "reason": "no_dob"}
        try:
            birth_date = datetime.fromisoformat(dob).date()
        except ValueError:
            return {"age_eligible": False, "confidence": 0.0, "reason": "invalid_dob_format"}
        today = datetime.now(timezone.utc).date()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return {
            "age_eligible": age >= 21,
            "age": age,
            "confidence": 0.95,
            "provider_reference": hashlib.sha256(f"{user_id}:{dob}".encode()).hexdigest()[:16],
        }


class OnfidoKYCAdapter(KYCAdapter):

    def __init__(self, api_token: str, base_url: str = "https://api.onfido.com/v3.6") -> None:
        super().__init__(IntegrationConfig(name="onfido", timeout_seconds=30.0))
        self._http = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Token token={api_token}"},
            timeout=30.0,
        )

    async def health_check(self) -> bool:
        try:
            r = await self._http.get("/ping")
            return r.status_code == 200
        except Exception:
            return False

    async def create_check(self, user_id: str, user_info: dict[str, Any]) -> dict[str, Any]:
        async def _do():
            applicant_response = await self._http.post(
                "/applicants",
                json={
                    "first_name": user_info.get("first_name", ""),
                    "last_name": user_info.get("last_name", ""),
                    "email": user_info.get("email", ""),
                    "dob": user_info.get("dob", ""),
                    "country": user_info.get("country", "IND"),
                },
            )
            applicant_response.raise_for_status()
            applicant_id = applicant_response.json()["id"]
            check_response = await self._http.post(
                "/checks",
                json={
                    "applicant_id": applicant_id,
                    "report_names": ["identity", "right_to_work", "document"],
                },
            )
            check_response.raise_for_status()
            return check_response.json()
        return await self.call_with_retry(_do)

    async def get_check_status(self, check_id: str) -> dict[str, Any]:
        async def _do():
            r = await self._http.get(f"/checks/{check_id}")
            r.raise_for_status()
            return r.json()
        return await self.call_with_retry(_do)

    async def verify_age(self, user_id: str, document_data: dict[str, Any]) -> dict[str, Any]:
        check = await self.create_check(user_id, document_data)
        return {
            "age_eligible": check.get("status") == "complete",
            "check_id": check.get("id"),
            "confidence": 0.9,
        }
