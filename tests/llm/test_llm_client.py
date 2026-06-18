import asyncio
from typing import TYPE_CHECKING, cast

import rag_service.llm.client as llm_client

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
