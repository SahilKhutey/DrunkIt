"""Background Event Worker process polling event_outbox and publishing to Kafka."""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from faccp_platform.database.session import get_session_manager
from faccp_platform.events.outbox import OutboxService
from faccp_platform.events.producer import EventProducer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("faccp.event-worker")


async def run() -> None:
    logger.info("Starting FACCP Event Worker...")
    producer = EventProducer()
    await producer.start()
    session_manager = get_session_manager()

    try:
        while True:
            try:
                async with session_manager.session() as session:
                    outbox = OutboxService(session=session, producer=producer)
                    processed = await outbox.process_pending(limit=50)
                    if processed > 0:
                        logger.info(f"Event Worker processed {processed} pending outbox events")
            except Exception as exc:
                logger.error(f"Error in Event Worker loop: {exc}")

            await asyncio.sleep(1.0)
    except asyncio.CancelledError:
        logger.info("Event Worker shutting down...")
    finally:
        await producer.stop()


def main() -> int:
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Event Worker terminated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
