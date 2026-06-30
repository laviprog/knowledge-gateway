import asyncio
from typing import TYPE_CHECKING, cast

import rag_service.llm.client as llm_client
from rag_service.llm.client import ProviderConfig

if TYPE_CHECKING:
    from openai import AsyncOpenAI


class FakeOpenAIClient:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


def test_close_llm_clients_closes_and_clears_registry(monkeypatch) -> None:
    fake_client = FakeOpenAIClient()
    config = ProviderConfig(
        base_url="http://example",
        api_key=None,
        timeout_seconds=30,
        max_retries=2,
    )
    monkeypatch.setattr(llm_client, "_clients", {config: cast("AsyncOpenAI", fake_client)})

    asyncio.run(llm_client.close_llm_clients())

    assert fake_client.closed is True
    assert llm_client._clients == {}


def test_get_llm_client_uses_configured_max_retries(monkeypatch) -> None:
    monkeypatch.setattr(llm_client, "_clients", {})
    config = ProviderConfig(
        base_url="http://example",
        api_key=None,
        timeout_seconds=30,
        max_retries=5,
    )

    client = llm_client.get_llm_client(config)

    assert client.max_retries == 5


def test_get_llm_client_reuses_client_per_config(monkeypatch) -> None:
    monkeypatch.setattr(llm_client, "_clients", {})
    config = ProviderConfig(
        base_url="http://example",
        api_key="secret",
        timeout_seconds=15,
        max_retries=1,
    )

    first = llm_client.get_llm_client(config)
    second = llm_client.get_llm_client(config)

    assert first is second
    assert str(first.base_url).rstrip("/") == "http://example"
