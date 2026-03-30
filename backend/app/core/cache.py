from functools import wraps

import redis.asyncio as redis

from app.core.config import settings

redis_client: redis.Redis | None = None


async def init_redis() -> None:
    global redis_client
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def cached(prefix: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator
