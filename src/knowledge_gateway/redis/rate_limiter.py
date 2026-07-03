import time
from uuid import UUID, uuid4

from knowledge_gateway.log_config import get_log
from knowledge_gateway.redis.client import get_redis_client

log = get_log(__name__)

_WINDOW_MS = 60_000  # 1 minute in milliseconds

# Atomically removes expired entries, counts remaining, and adds the current
# request if within the limit. Returns 0 (allowed) or 1 (blocked).
_SLIDING_WINDOW_SCRIPT = """
local key = KEYS[1]
local now_ms = tonumber(ARGV[1])
local window_ms = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local member = ARGV[4]

redis.call('ZREMRANGEBYSCORE', key, 0, now_ms - window_ms)
local count = redis.call('ZCARD', key)

if count < limit then
    redis.call('ZADD', key, now_ms, member)
    redis.call('PEXPIRE', key, window_ms)
    return 0
else
    return 1
end
"""


async def is_rate_limited(user_id: UUID, requests_per_minute: int) -> bool:
    """
    Sliding-window rate limiter keyed by user_id.

    Uses a Redis sorted set where each member is a unique request token
    and the score is the request timestamp in milliseconds. Expired entries
    (older than one minute) are pruned atomically before each check.

    Returns True if the request should be blocked (limit exceeded).
    Returns False (allow) on Redis errors to avoid blocking legitimate traffic.
    """
    if requests_per_minute <= 0:
        return False

    client = get_redis_client()
    now_ms = int(time.time() * 1000)
    key = f"rl:{user_id}"
    member = f"{now_ms}:{uuid4().hex}"

    try:
        result = await client.eval(
            _SLIDING_WINDOW_SCRIPT,
            1,
            key,
            str(now_ms),
            str(_WINDOW_MS),
            str(requests_per_minute),
            member,
        )
        return bool(result)
    except Exception:
        log.warning("Redis rate limit check failed, allowing request", user_id=str(user_id))
        return False
