import hashlib
import secrets
from uuid import UUID

from knowledge_gateway.config import settings
from knowledge_gateway.log_config import get_log
from knowledge_gateway.redis.client import get_redis_client

log = get_log(__name__)

_KEY_PREFIX = "session:"


def _redis_key(raw_token: str) -> str:
    """
    Derive the Redis key from a raw session token.

    The token is hashed (SHA-256) before use so a Redis dump never exposes usable session
    credentials — mirroring how API keys are stored.
    """
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    return f"{_KEY_PREFIX}{token_hash}"


async def create_session(user_id: UUID) -> str:
    """
    Create a new session for the user and return the raw (opaque) token to hand to the client.
    """
    raw_token = secrets.token_urlsafe(32)
    client = get_redis_client()
    await client.set(_redis_key(raw_token), str(user_id), ex=settings.SESSION_TTL_SECONDS)
    return raw_token


async def resolve_session_user_id(raw_token: str) -> UUID | None:
    """
    Return the user id for a valid session token, sliding its TTL forward. Returns None for an
    unknown/expired token. Fails closed (returns None) on Redis errors, unlike the rate limiter —
    an unreachable session store must not grant access.
    """
    if not raw_token:
        return None

    client = get_redis_client()
    key = _redis_key(raw_token)
    try:
        user_id = await client.get(key)
        if user_id is None:
            return None
        await client.expire(key, settings.SESSION_TTL_SECONDS)
        # decode_responses=True yields str at runtime; guard bytes for the type checker.
        return UUID(user_id.decode() if isinstance(user_id, bytes) else user_id)
    except Exception:
        log.warning("Redis session lookup failed, denying session")
        return None


async def delete_session(raw_token: str) -> None:
    """
    Delete a session (logout). No-op for an empty token or on Redis errors.
    """
    if not raw_token:
        return

    client = get_redis_client()
    try:
        await client.delete(_redis_key(raw_token))
    except Exception:
        log.warning("Redis session deletion failed")
