from redis.asyncio import Redis


redis = Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)


async def health_check():

    return await redis.ping()
