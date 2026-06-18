import asyncio
from typing import TYPE_CHECKING, cast

import rag_service.llm.client as llm_client
from rag_service.config import settings

if TYPE_CHECKING:
    from openai import AsyncOpenAI


class FakeOpenAIClient:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


def test_close_llm_client_closes_and_resets_shared_client(monkeypatch) -> None:
    fake_client = FakeOpenAIClient()
    monkeypatch.setattr(llm_client, "_client", cast("AsyncOpenAI", fake_client))

    asyncio.run(llm_client.close_llm_client())

    assert fake_client.closed is True
    assert llm_client._client is None


def test_get_llm_client_uses_configured_max_retries(monkeypatch) -> None:
    monkeypatch.setattr(llm_client, "_client", None)
    monkeypatch.setattr(settings, "LLM_MAX_RETRIES", 5)

    client = llm_client.get_llm_client()

    assert client.max_retries == 5
