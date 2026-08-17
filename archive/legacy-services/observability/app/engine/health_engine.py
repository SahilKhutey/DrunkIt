from services.observability.app.collectors.health_collectors import (
    database_health,
    kafka_health,
    redis_health,
)


class HealthEngine:

    def __init__(self, db_client=None, redis_client=None, kafka_client=None):
        self.db_client = db_client
        self.redis_client = redis_client
        self.kafka_client = kafka_client

    async def evaluate(self) -> dict:
        checks = {
            "database": await database_health(self.db_client),
            "redis": await redis_health(self.redis_client),
            "kafka": await kafka_health(self.kafka_client),
        }

        failed = [name for name, status in checks.items() if not status]

        if not failed:
            status = "healthy"
        elif len(failed) == len(checks):
            status = "unhealthy"
        else:
            status = "degraded"

        return {
            "status": status,
            "checks": checks,
            "failed": failed,
        }
