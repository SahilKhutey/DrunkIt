from datetime import datetime, timezone
from services.observability.app.engine.health_engine import HealthEngine


class HealthService:

    def __init__(self, health_engine: HealthEngine | None = None):
        self.health_engine = health_engine or HealthEngine()
        self.services_health: dict[str, dict] = {
            "api-gateway": {"service_name": "api-gateway", "status": "healthy", "latency_ms": 42.0, "error_rate": 0.001},
            "order-service": {"service_name": "order-service", "status": "healthy", "latency_ms": 81.0, "error_rate": 0.002},
            "payment-service": {"service_name": "payment-service", "status": "healthy", "latency_ms": 120.0, "error_rate": 0.005},
            "compliance-service": {"service_name": "compliance-service", "status": "healthy", "latency_ms": 35.0, "error_rate": 0.0},
            "security-service": {"service_name": "security-service", "status": "healthy", "latency_ms": 28.0, "error_rate": 0.0},
            "inventory-service": {"service_name": "inventory-service", "status": "healthy", "latency_ms": 45.0, "error_rate": 0.001},
            "delivery-service": {"service_name": "delivery-service", "status": "healthy", "latency_ms": 73.0, "error_rate": 0.003},
        }

    async def get_system_health() -> dict:
        return await self.health_engine.evaluate()

    async def get_all_services() -> list[dict]:
        return list(self.services_health.values())

    async def get_service_health(self, service_name: str) -> dict | None:
        return self.services_health.get(service_name)
