"""
Background worker framework using Kafka as the queue.
"""

from __future__ import annotations

import asyncio
import functools
from typing import Callable

from faccp_common.events import make_event
from faccp_common.kafka_client import EventConsumer, EventProducer
from faccp_common.logging import get_logger

logger = get_logger(__name__)


def worker(topic: str, group_id: str):
    """
    Decorator: turns an async function into a Kafka-backed worker.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            from app.config import get_settings
            settings = get_settings()
            consumer = EventConsumer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                group_id=group_id, topics=[topic],
                client_id=f"{group_id}-worker",
            )
            await consumer.start()
            logger.info("worker.started", topic=topic, group_id=group_id)
            try:
                async for msg_topic, key, value in consumer.consume():
                    try:
                        await func(value, *args, **kwargs)
                    except Exception:
                        logger.exception("worker.handler_failed", topic=msg_topic, key=key)
            finally:
                await consumer.stop()
        return wrapper
    return decorator


async def publish_delayed(topic: str, payload: dict, delay_seconds: float) -> None:
    """Publish a message after a delay (for retries, scheduled tasks)."""
    await asyncio.sleep(delay_seconds)
    from app.config import get_settings
    settings = get_settings()
    producer = EventProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        client_id="delayed-publisher",
    )
    await producer.start()
    try:
        event = make_event(event_type="delayed.publish", payload=payload, producer="delayed-publisher")
        await producer.publish(topic=topic, payload=event)
    finally:
        await producer.stop()
