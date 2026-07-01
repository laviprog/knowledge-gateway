from uuid import uuid4

import pytest

from rag_service.auth import session_store


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}
        self.expires: dict[str, int] = {}

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self.store[key] = value
        if ex is not None:
            self.expires[key] = ex

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def expire(self, key: str, ttl: int) -> None:
        if key in self.store:
            self.expires[key] = ttl

    async def delete(self, key: str) -> None:
        self.store.pop(key, None)
        self.expires.pop(key, None)


@pytest.fixture
def fake_redis(monkeypatch: pytest.MonkeyPatch) -> FakeRedis:
    fake = FakeRedis()
    monkeypatch.setattr(session_store, "get_redis_client", lambda: fake)
    return fake


@pytest.mark.anyio
async def test_create_and_resolve_session(fake_redis: FakeRedis) -> None:
    user_id = uuid4()

    token = await session_store.create_session(user_id)
    resolved = await session_store.resolve_session_user_id(token)

    assert resolved == user_id
    # The raw token must not be stored verbatim (it is hashed).
    assert token not in fake_redis.store


@pytest.mark.anyio
async def test_resolve_slides_ttl(fake_redis: FakeRedis) -> None:
    token = await session_store.create_session(uuid4())
    fake_redis.expires.clear()

    await session_store.resolve_session_user_id(token)

    assert len(fake_redis.expires) == 1


@pytest.mark.anyio
async def test_resolve_unknown_token_returns_none(fake_redis: FakeRedis) -> None:
    assert await session_store.resolve_session_user_id("nope") is None


@pytest.mark.anyio
async def test_resolve_empty_token_returns_none(fake_redis: FakeRedis) -> None:
    assert await session_store.resolve_session_user_id("") is None


@pytest.mark.anyio
async def test_delete_session(fake_redis: FakeRedis) -> None:
    token = await session_store.create_session(uuid4())

    await session_store.delete_session(token)

    assert await session_store.resolve_session_user_id(token) is None
