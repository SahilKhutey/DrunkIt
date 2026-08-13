async def database_health(db_client=None) -> bool:
    if db_client is None:
        return True
    try:
        if hasattr(db_client, "execute"):
            await db_client.execute("SELECT 1")
        return True
    except Exception:
        return False


async def redis_health(redis_client=None) -> bool:
    if redis_client is None:
        return True
    try:
        if hasattr(redis_client, "ping"):
            res = await redis_client.ping()
            return res is True
        return True
    except Exception:
        return False


async def kafka_health(kafka_client=None) -> bool:
    if kafka_client is None:
        return True
    try:
        if hasattr(kafka_client, "fetch_metadata"):
            meta = await kafka_client.fetch_metadata()
            return bool(meta and getattr(meta, "brokers", None))
        return True
    except Exception:
        return False
