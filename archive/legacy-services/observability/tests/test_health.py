import pytest
from services.observability.app.engine.health_engine import HealthEngine


@pytest.mark.asyncio
async def test_health_engine_evaluation():
    engine = HealthEngine()
    res = await engine.evaluate()
    assert res["status"] in ("healthy", "degraded", "unhealthy")
    assert "checks" in res
    assert "database" in res["checks"]
    assert "redis" in res["checks"]
    assert "kafka" in res["checks"]
