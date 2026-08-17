from datetime import datetime, timezone
from services.resilience.app.models.enums import PlatformMode


class EmergencyController:

    def __init__(self):
        self.mode = PlatformMode.NORMAL
        self.events: list[dict] = []

    def activate(self, actor: str = "sysadmin", reason: str = "EMERGENCY_TRIGGERED") -> dict:
        self.mode = PlatformMode.EMERGENCY
        rec = {
            "actor": actor,
            "action": "EMERGENCY_ACTIVATE",
            "reason": reason,
            "timestamp": datetime.now(timezone.utc),
        }
        self.events.append(rec)
        return rec

    def deactivate(self, actor: str = "sysadmin") -> dict:
        self.mode = PlatformMode.NORMAL
        rec = {
            "actor": actor,
            "action": "EMERGENCY_DEACTIVATE",
            "reason": "OPERATIONS_NORMALIZED",
            "timestamp": datetime.now(timezone.utc),
        }
        self.events.append(rec)
        return rec


class ContinuityService:

    def __init__(self):
        self.controller = EmergencyController()

    async def get_status(self) -> dict:
        return {
            "platform_mode": self.controller.mode.value,
            "rpo_status": "WITHIN_TARGET",
            "rto_status": "WITHIN_TARGET",
            "rpo_minutes": 5,
            "rto_minutes": 15,
        }

    async def enable_emergency(self, actor: str, reason: str) -> dict:
        return self.controller.activate(actor, reason)

    async def disable_emergency(self, actor: str) -> dict:
        return self.controller.deactivate(actor)
