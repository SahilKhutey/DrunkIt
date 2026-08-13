from datetime import datetime, timezone
from uuid import uuid4


class DeviceService:

    def __init__(self):
        self.devices: dict[str, dict] = {}
        self.device_users: dict[str, set[str]] = {}

    async def register_device(self, device_reference: str, platform: str = "ANDROID", app_version: str = "1.0.0") -> dict:
        if device_reference in self.devices:
            return self.devices[device_reference]

        dev = {
            "id": str(uuid4()),
            "device_reference": device_reference,
            "platform": platform,
            "app_version": app_version,
            "status": "ACTIVE",
            "created_at": datetime.now(timezone.utc),
        }
        self.devices[device_reference] = dev
        return dev

    async def link_user(self, device_reference: str, user_id: str) -> dict | None:
        dev = await self.register_device(device_reference)
        users = self.device_users.setdefault(device_reference, set())
        users.add(user_id)

        signal = None
        if len(users) >= 3:
            signal = {"signal_type": "MULTI_ACCOUNT_DEVICE", "severity": "MEDIUM", "score": 20.0}

        return {"device": dev, "linked_users_count": len(users), "risk_signal": signal}

    async def get_device(self, device_id: str) -> dict | None:
        for d in self.devices.values():
            if d["id"] == device_id or d["device_reference"] == device_id:
                return d
        return None
