"""
Unit tests for Phase D5 Redis Keys & Idempotency Service.
"""

from __future__ import annotations

import os
import sys
from unittest.mock import AsyncMock, patch
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from packages.cache.keys import RedisKey
from packages.idempotency.service import IdempotencyService


def test_redis_keys_builder():
    assert RedisKey.driver_location("drv_10") == "driver:location:drv_10"
    assert RedisKey.driver_status("drv_10") == "driver:status:drv_10"
    assert RedisKey.idempotency("key_abc") == "idempotency:key_abc"
    assert RedisKey.delivery("del_50") == "delivery:del_50"


@pytest.mark.asyncio
async def test_idempotency_service_get_and_save():
    service = IdempotencyService()

    with patch("packages.idempotency.service.redis") as mock_redis:
        mock_redis.get = AsyncMock(return_value='{"status": "SUCCESS", "order_id": "ORD-123"}')
        mock_redis.set = AsyncMock(return_value=True)

        res = await service.get("test-idempotency-key")
        assert res == {"status": "SUCCESS", "order_id": "ORD-123"}

        await service.save("test-idempotency-key", {"status": "SUCCESS"})
        assert mock_redis.set.called
