from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

import rag_service.chats.routes as chats_routes
from rag_service.api_keys.dependencies import provide_api_key_service
from rag_service.main import app
from rag_service.security.dependencies import AuthContext, require_user_key

_CHAT_URL = "/chat/completions"
_VALID_PAYLOAD = {
    "model": "llama3",
    "messages": [{"role": "user", "content": "Hello"}],
}


class _NullApiKeyService:
    async def validate_api_key(self, api_key: str) -> None:
        return None


async def _null_api_key_service():
    yield _NullApiKeyService()


@pytest.mark.anyio
async def test_chat_completion_returns_401_when_no_authorization_header() -> None:
    app.dependency_overrides[provide_api_key_service] = _null_api_key_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(_CHAT_URL, json=_VALID_PAYLOAD)
    finally:
        app.dependency_overrides.pop(provide_api_key_service, None)

    assert response.status_code == 401


@pytest.mark.anyio
async def test_chat_completion_returns_401_when_api_key_is_invalid() -> None:
    app.dependency_overrides[provide_api_key_service] = _null_api_key_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                _CHAT_URL,
                json=_VALID_PAYLOAD,
                headers={"Authorization": "Bearer wrong-key"},
            )
    finally:
        app.dependency_overrides.pop(provide_api_key_service, None)

    assert response.status_code == 401


@pytest.mark.anyio
async def test_chat_completion_returns_429_when_rate_limited(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    auth = AuthContext(user_id=uuid4(), api_key_id=uuid4(), requests_per_minute=10)

    async def always_rate_limited(user_id, requests_per_minute) -> bool:
        return True

    monkeypatch.setattr(chats_routes, "is_rate_limited", always_rate_limited)
    app.dependency_overrides[require_user_key] = lambda: auth
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                _CHAT_URL,
                json=_VALID_PAYLOAD,
                headers={"Authorization": "Bearer dummy"},
            )
    finally:
        app.dependency_overrides.pop(require_user_key, None)

    assert response.status_code == 429
    body = response.json()
    assert body["error"]["code"] == "rate_limit_exceeded"
    assert body["error"]["type"] == "rate_limit_error"
