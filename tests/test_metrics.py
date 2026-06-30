import pytest
from httpx import ASGITransport, AsyncClient
from prometheus_client import generate_latest

from rag_service import metrics
from rag_service.main import app


@pytest.mark.anyio
async def test_metrics_endpoint_exposes_prometheus_format() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/metrics")

    assert response.status_code == 200
    assert "# HELP" in response.text


def test_custom_collectors_are_registered() -> None:
    metrics.chat_completions_total.labels(model="m", outcome="succeeded").inc()
    metrics.chat_tokens_total.labels(model="m", kind="prompt").inc(10)
    metrics.llm_provider_errors_total.labels(type="timeout").inc()

    output = generate_latest().decode()

    assert "rag_chat_completions_total" in output
    assert "rag_chat_tokens_total" in output
    assert "rag_llm_provider_errors_total" in output
