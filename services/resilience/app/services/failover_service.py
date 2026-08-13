from services.resilience.app.engine.failover_engine import FailoverEngine


class FailoverService:

    def __init__(self, failover_engine: FailoverEngine | None = None):
        self.failover_engine = failover_engine or FailoverEngine()
        self.operations: dict[str, dict] = {}

    async def execute_failover(self, service: str, primary: str = "region-a", secondary: str = "region-b") -> dict:
        res = await self.failover_engine.failover(service, primary, secondary)
        self.operations[service] = res
        return res

    async def get_failover_status(self, service: str) -> dict | None:
        return self.operations.get(service, {"service": service, "status": "NORMAL", "active": "region-a"})
