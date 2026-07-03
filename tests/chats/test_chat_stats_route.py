from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from knowledge_gateway.chats.dependencies import provide_chat_completion_request_log_service
from knowledge_gateway.chats.models import ChatCompletionRequestStatus
from knowledge_gateway.chats.schema import (
    ChatCompletionModelStats,
    ChatCompletionStats,
    ChatCompletionStatusCount,
)
from knowledge_gateway.main import app
from knowledge_gateway.security.dependencies import AuthContext, require_admin

_STATS_URL = "/chat-completion-requests/stats"

_CANNED_STATS = ChatCompletionStats(
    total_requests=3,
    retrieval_requests=2,
    by_status=[
        ChatCompletionStatusCount(status=ChatCompletionRequestStatus.SUCCEEDED, count=2),
        ChatCompletionStatusCount(status=ChatCompletionRequestStatus.FAILED, count=1),
    ],
    prompt_tokens_total=100,
    completion_tokens_total=50,
    total_tokens_total=150,
    avg_embedding_ms=1.5,
    avg_llm_ttfb_ms=10.0,
    avg_llm_generation_ms=20.0,
    avg_total_ms=35.0,
    by_model=[
        ChatCompletionModelStats(
            model_public_id="rag-assistant-lite",
            requests=3,
            total_tokens=150,
            avg_total_ms=35.0,
        )
    ],
    by_knowledge_base=[],
)


class _FakeStatsService:
    def __init__(self) -> None:
        self.kwargs: dict | None = None

    async def get_stats(self, **kwargs) -> ChatCompletionStats:
        self.kwargs = kwargs
        return _CANNED_STATS


@pytest.mark.anyio
async def test_stats_endpoint_returns_aggregates_and_forwards_filters() -> None:
    fake_service = _FakeStatsService()

    async def _provide_fake_service():
        yield fake_service

    auth = AuthContext(user_id=uuid4(), api_key_id=uuid4(), requests_per_minute=0)
    app.dependency_overrides[require_admin] = lambda: auth
    app.dependency_overrides[provide_chat_completion_request_log_service] = _provide_fake_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                _STATS_URL,
                params={"model": "rag-assistant-lite"},
                headers={"Authorization": "Bearer dummy"},
            )
    finally:
        app.dependency_overrides.pop(require_admin, None)
        app.dependency_overrides.pop(provide_chat_completion_request_log_service, None)

    assert response.status_code == 200
    body = response.json()
    assert body["total_requests"] == 3
    assert body["total_tokens_total"] == 150
    assert len(body["by_status"]) == 2
    assert body["by_model"][0]["model_public_id"] == "rag-assistant-lite"
    # Query filters are forwarded to the service.
    assert fake_service.kwargs is not None
    assert fake_service.kwargs["model"] == "rag-assistant-lite"
