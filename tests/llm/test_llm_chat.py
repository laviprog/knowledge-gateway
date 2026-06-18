import asyncio
from collections.abc import AsyncIterator
from types import SimpleNamespace

import httpx
import openai
import pytest

from rag_service.llm.base import ProviderTimeoutError
from rag_service.llm.chat import OpenAIChatClient


class FakeStream:
    def __init__(self, chunks: list[SimpleNamespace]) -> None:
        self._chunks = chunks

    async def __aiter__(self) -> AsyncIterator[SimpleNamespace]:
        for chunk in self._chunks:
            yield chunk


class FakeCompletions:
    def __init__(self, chunks: list[SimpleNamespace]) -> None:
        self._chunks = chunks
        self.kwargs: dict | None = None

    async def create(self, **kwargs):
        self.kwargs = kwargs
        return FakeStream(self._chunks)


def make_content_chunk(content: str, finish_reason: str | None = None) -> SimpleNamespace:
    delta = SimpleNamespace(content=content)
    choice = SimpleNamespace(delta=delta, finish_reason=finish_reason)
    return SimpleNamespace(choices=[choice], usage=None)


def make_usage_chunk(prompt_tokens: int, completion_tokens: int) -> SimpleNamespace:
    # Final usage chunk carries empty choices, like real OpenAI streaming.
    usage = SimpleNamespace(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)
    return SimpleNamespace(choices=[], usage=usage)


def build_client(chunks: list[SimpleNamespace]) -> tuple[OpenAIChatClient, FakeCompletions]:
    client = OpenAIChatClient()
    completions = FakeCompletions(chunks)
    fake = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    client.client = fake  # ty: ignore[invalid-assignment]
    return client, completions


def test_stream_chat_maps_content_and_final_usage_chunk() -> None:
    chunks = [
        make_content_chunk("Hello"),
        make_content_chunk("!", finish_reason="stop"),
        make_usage_chunk(prompt_tokens=10, completion_tokens=2),
    ]
    client, completions = build_client(chunks)

    async def collect():
        return [
            chunk
            async for chunk in client.stream_chat(
                model="m",
                messages=[{"role": "user", "content": "hi"}],
                temperature=0.3,
                max_completion_tokens=128,
            )
        ]

    result = asyncio.run(collect())

    assert [c.content for c in result] == ["Hello", "!", ""]
    assert result[1].finish_reason == "stop"
    assert result[-1].prompt_tokens == 10
    assert result[-1].completion_tokens == 2
    # Streaming and usage are always requested; optional params are forwarded.
    assert completions.kwargs is not None
    assert completions.kwargs["stream"] is True
    assert completions.kwargs["stream_options"] == {"include_usage": True}
    assert completions.kwargs["temperature"] == 0.3
    assert completions.kwargs["max_completion_tokens"] == 128


def test_stream_chat_raises_provider_timeout() -> None:
    client = OpenAIChatClient()

    class TimeoutCompletions:
        async def create(self, **kwargs):
            raise openai.APITimeoutError(request=httpx.Request("POST", "http://test"))

    fake = SimpleNamespace(chat=SimpleNamespace(completions=TimeoutCompletions()))
    client.client = fake  # ty: ignore[invalid-assignment]

    async def collect():
        return [chunk async for chunk in client.stream_chat(model="m", messages=[])]

    with pytest.raises(ProviderTimeoutError):
        asyncio.run(collect())
