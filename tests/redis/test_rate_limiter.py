import asyncio
from uuid import uuid4

import pytest

import knowledge_gateway.redis.rate_limiter as rate_limiter_module
from knowledge_gateway.redis.rate_limiter import is_rate_limited


class FakeRedisClient:
    def __init__(self, eval_return: int = 0) -> None:
        self._eval_return = eval_return
        self.eval_calls: list[dict] = []

    async def eval(self, script: str, numkeys: int, *args: str) -> int:
        self.eval_calls.append({"numkeys": numkeys, "args": list(args)})
        return self._eval_return


class BrokenRedisClient:
    async def eval(self, *args, **kwargs) -> int:
        raise ConnectionError("Redis unavailable")


def test_is_rate_limited_returns_false_when_under_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeRedisClient(eval_return=0)
    monkeypatch.setattr(rate_limiter_module, "get_redis_client", lambda: fake)
    user_id = uuid4()

    result = asyncio.run(is_rate_limited(user_id, requests_per_minute=60))

    assert result is False
    assert len(fake.eval_calls) == 1


def test_is_rate_limited_returns_true_when_over_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeRedisClient(eval_return=1)
    monkeypatch.setattr(rate_limiter_module, "get_redis_client", lambda: fake)
    user_id = uuid4()

    result = asyncio.run(is_rate_limited(user_id, requests_per_minute=60))

    assert result is True


def test_is_rate_limited_skips_redis_when_unlimited(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeRedisClient()
    monkeypatch.setattr(rate_limiter_module, "get_redis_client", lambda: fake)
    user_id = uuid4()

    result = asyncio.run(is_rate_limited(user_id, requests_per_minute=0))

    assert result is False
    assert len(fake.eval_calls) == 0


def test_is_rate_limited_fails_open_on_redis_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rate_limiter_module, "get_redis_client", lambda: BrokenRedisClient())
    user_id = uuid4()

    result = asyncio.run(is_rate_limited(user_id, requests_per_minute=60))

    assert result is False


def test_is_rate_limited_passes_correct_key_and_window(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeRedisClient(eval_return=0)
    monkeypatch.setattr(rate_limiter_module, "get_redis_client", lambda: fake)
    user_id = uuid4()

    asyncio.run(is_rate_limited(user_id, requests_per_minute=30))

    call_args = fake.eval_calls[0]["args"]
    assert call_args[0] == f"rl:{user_id}"  # key
    assert call_args[2] == "60000"  # window_ms = 1 minute
    assert call_args[3] == "30"  # limit
    assert call_args[4].endswith(call_args[4][-32:])  # member has hex suffix


def test_is_rate_limited_uses_unique_member_per_call(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeRedisClient(eval_return=0)
    monkeypatch.setattr(rate_limiter_module, "get_redis_client", lambda: fake)
    user_id = uuid4()

    asyncio.run(is_rate_limited(user_id, requests_per_minute=60))
    asyncio.run(is_rate_limited(user_id, requests_per_minute=60))

    member_first = fake.eval_calls[0]["args"][4]
    member_second = fake.eval_calls[1]["args"][4]
    assert member_first != member_second
