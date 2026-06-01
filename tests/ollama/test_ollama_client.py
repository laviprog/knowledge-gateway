import asyncio
from typing import TYPE_CHECKING, cast

import rag_service.ollama.client as ollama_client

if TYPE_CHECKING:
    from ollama import AsyncClient


class FakeOllamaClient:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


def test_close_ollama_client_closes_and_resets_shared_client(monkeypatch) -> None:
    fake_client = FakeOllamaClient()
    monkeypatch.setattr(ollama_client, "_client", cast("AsyncClient", fake_client))

    asyncio.run(ollama_client.close_ollama_client())

    assert fake_client.closed is True
    assert ollama_client._client is None
