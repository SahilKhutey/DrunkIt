from packages.cache.keys import RedisKey
from packages.cache.redis import redis


async def update_driver_location(
    driver_id: str,
    latitude: float,
    longitude: float,
):

    key = RedisKey.driver_location(
        driver_id
    )

    await redis.hset(
        key,
        mapping={
            "latitude": latitude,
            "longitude": longitude,
        },
    )

    await redis.expire(
        key,
        120,
    )


async def index_driver(
    driver_id: str,
    latitude: float,
    longitude: float,
):

    await redis.geoadd(
        "drivers:geo",
        (
            longitude,
            latitude,
            driver_id,
        ),
    )


async def nearby_drivers(
    latitude: float,
    longitude: float,
    radius_km: float = 5,
):

    return await redis.geosearch(
        "drivers:geo",
        longitude=longitude,
        latitude=latitude,
        radius=radius_km,
        unit="km",
    )


async def set_driver_status(
    driver_id: str,
    status: str,
):

    await redis.set(
        RedisKey.driver_status(
            driver_id
        ),
        status,
        ex=300,
    )


async def cache_delivery_state(
    delivery_id: str,
    status: str,
):

    key = (
        f"delivery:state:{delivery_id}"
    )

    await redis.hset(
        key,
        mapping={
            "status": status,
        },
    )

    await redis.expire(
        key,
        3600,
    )
