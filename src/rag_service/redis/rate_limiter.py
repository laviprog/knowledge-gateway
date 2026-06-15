import time
from uuid import UUID

from rag_service.log_config import get_log
from rag_service.redis.client import get_redis_client

log = get_log(__name__)

_WINDOW_SECONDS = 60


async def is_rate_limited(user_id: UUID, requests_per_minute: int) -> bool:
    """
    Fixed-window rate limiter keyed by user_id.

    Returns True if the request should be blocked (limit exceeded).
    Returns False (allow) on Redis errors to avoid blocking legitimate traffic.
    """
    if requests_per_minute <= 0:
        return False

    client = get_redis_client()
    window = int(time.time()) // _WINDOW_SECONDS
    key = f"rl:{user_id}:{window}"

    try:
        count = await client.incr(key)  # ty: ignore[invalid-await]
        if count == 1:
            await client.expire(key, _WINDOW_SECONDS)
        return count > requests_per_minute
    except Exception:
        log.warning("Redis rate limit check failed, allowing request", user_id=str(user_id))
        return False
