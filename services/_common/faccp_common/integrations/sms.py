"""SMS provider integration adapters."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

import httpx

from faccp_common.integrations.base import IntegrationAdapter, IntegrationConfig
from faccp_common.logging import get_logger

logger = get_logger(__name__)


class SMSAdapter(IntegrationAdapter):
    @abstractmethod
    async def send(self, to_phone: str, message: str, **kwargs) -> dict[str, Any]:
        ...


class StubSMSAdapter(SMSAdapter):
    def __init__(self) -> None:
        super().__init__(IntegrationConfig(name="stub_sms"))
    async def health_check(self) -> bool: return True
    async def send(self, to_phone: str, message: str, **kwargs) -> dict[str, Any]:
        logger.info("sms.stub.sent", to=to_phone, message_preview=message[:50])
        return {"status": "sent", "to": to_phone, "provider": "stub"}


class TwilioSMSAdapter(SMSAdapter):
    def __init__(self, account_sid: str, auth_token: str, from_number: str) -> None:
        super().__init__(IntegrationConfig(name="twilio"))
        self._http = httpx.AsyncClient(
            base_url=f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}",
            auth=(account_sid, auth_token),
            timeout=30.0,
        )
        self.from_number = from_number

    async def health_check(self) -> bool:
        try:
            r = await self._http.get("/Messages.json", params={"PageSize": 1})
            return r.status_code == 200
        except Exception: return False

    async def send(self, to_phone: str, message: str, **kwargs) -> dict[str, Any]:
        async def _do():
            r = await self._http.post(
                "/Messages.json",
                data={"From": self.from_number, "To": to_phone, "Body": message},
            )
            r.raise_for_status()
            return r.json()
        return await self.call_with_retry(_do)
