import pytest
from services.security.app.engine.velocity_engine import VelocityEngine


@pytest.mark.asyncio
async def test_order_velocity_spike():
    engine = VelocityEngine()
    consumer_id = "cons-vel-100"

    for _ in range(4):
        sig = await engine.check_order_velocity(consumer_id)
        assert sig is None

    # 5th attempt triggers MEDIUM velocity signal
    sig_med = await engine.check_order_velocity(consumer_id)
    assert sig_med["signal_type"] == "ORDER_VELOCITY"
    assert sig_med["severity"] == "MEDIUM"

    for _ in range(4):
        await engine.check_order_velocity(consumer_id)

    # 10th attempt triggers HIGH velocity signal
    sig_high = await engine.check_order_velocity(consumer_id)
    assert sig_high["severity"] == "HIGH"
