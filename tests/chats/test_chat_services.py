import asyncio
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, cast

from rag_service.chats.schema import ChatCompletionRequest
from rag_service.chats.services import ChatCompletionService, ChatCompletionTimeoutError
from rag_service.config import settings
from rag_service.documents.services import (
    DocumentSearchTimings,
    DocumentSearchWithMetrics,
)
from rag_service.llm_models.models import LlmModel
from rag_service.ollama.chat import OllamaChatChunk, OllamaTimeoutError
from rag_service.qdrant.schema import VectorSearchResult

if TYPE_CHECKING:
    from rag_service.documents.services import DocumentService
    from rag_service.llm_models.services import LlmModelService
    from rag_service.ollama.chat import OllamaChatClient


class FakeDocumentService:
    def __init__(self) -> None:
        self.query: str | None = None
        self.limit: int | None = None

    async def search_documents_with_metrics(
        self,
        query: str,
        limit: int,
    ) -> DocumentSearchWithMetrics:
        self.query = query
        self.limit = limit
        return DocumentSearchWithMetrics(
            results=[
                VectorSearchResult(
                    score=0.9,
                    document_id="document-id",
                    chunk_id="chunk-id",
                    chunk_index=0,
                    content="Knowledge base answer.",
                )
            ],
            timings=DocumentSearchTimings(
                ollama_embedding_ms=1.0,
                qdrant_search_ms=2.0,
                total_ms=3.0,
            ),
        )


class FakeLlmModelService:
    async def get_by_public_id_or_raise(self, public_id: str) -> LlmModel:
        return LlmModel(
            public_id=public_id,
            provider="ollama",
            provider_model="llama3.1:8b",
            context_window_tokens=8192,
            max_completion_tokens=1024,
            description=None,
        )


class FakeOllamaChatClient:
    def __init__(self) -> None:
        self.model: str | None = None
        self.messages: list[dict[str, str]] = []
        self.think: bool | str | None = None

    async def stream_chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        top_p: float | None = None,
        max_completion_tokens: int | None = None,
        think: bool | str | None = False,
    ) -> AsyncIterator[OllamaChatChunk]:
        self.model = model
        self.messages = messages
        self.think = think
        yield OllamaChatChunk(
            content="Hello",
            done=False,
            finish_reason=None,
            prompt_tokens=None,
            completion_tokens=None,
        )
        yield OllamaChatChunk(
            content="!",
            done=True,
            finish_reason="stop",
            prompt_tokens=10,
            completion_tokens=2,
        )


class FakeTimeoutOllamaChatClient:
    async def stream_chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        top_p: float | None = None,
        max_completion_tokens: int | None = None,
        think: bool | str | None = False,
    ) -> AsyncIterator[OllamaChatChunk]:
        raise OllamaTimeoutError("Ollama request timed out")
        yield OllamaChatChunk(
            content="",
            done=True,
            finish_reason="stop",
            prompt_tokens=None,
            completion_tokens=None,
        )


def test_prepare_completion_builds_retrieval_and_prompt() -> None:
    document_service = FakeDocumentService()
    chat_client = FakeOllamaChatClient()
    service = ChatCompletionService(
        document_service=cast("DocumentService", document_service),
        llm_model_service=cast("LlmModelService", FakeLlmModelService()),
        chat_client=cast("OllamaChatClient", chat_client),
    )
    request = ChatCompletionRequest.model_validate(
        {
            "model": "rag-assistant-lite",
            "messages": [{"role": "user", "content": "What is the answer?"}],
        }
    )

    plan = asyncio.run(service.prepare_completion(request))

    assert document_service.query == "What is the answer?"
    assert document_service.limit == settings.RAG_RETRIEVAL_LIMIT
    assert plan.llm_model.provider_model == "llama3.1:8b"
    assert "Knowledge base answer." in plan.ollama_messages[0]["content"]


def test_stream_completion_returns_openai_sse_events() -> None:
    chat_client = FakeOllamaChatClient()
    service = ChatCompletionService(
        document_service=cast("DocumentService", FakeDocumentService()),
        llm_model_service=cast("LlmModelService", FakeLlmModelService()),
        chat_client=cast("OllamaChatClient", chat_client),
    )
    request = ChatCompletionRequest.model_validate(
        {
            "model": "rag-assistant-lite",
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": True,
            "stream_options": {"include_usage": True},
            "think": False,
        }
    )

    async def collect_events() -> list[str]:
        plan = await service.prepare_completion(request)
        return [event async for event in service.stream_completion(plan)]

    events = asyncio.run(collect_events())

    assert events[0].startswith("data: ")
    assert '"role": "assistant"' in events[0]
    assert any('"content": "Hello"' in event for event in events)
    assert any('"usage"' in event for event in events)
    assert events[-1] == "data: [DONE]\n\n"
    assert chat_client.model == "llama3.1:8b"
    assert chat_client.think is False


def test_complete_returns_non_stream_response() -> None:
    service = ChatCompletionService(
        document_service=cast("DocumentService", FakeDocumentService()),
        llm_model_service=cast("LlmModelService", FakeLlmModelService()),
        chat_client=cast("OllamaChatClient", FakeOllamaChatClient()),
    )
    request = ChatCompletionRequest.model_validate(
        {
            "model": "rag-assistant-lite",
            "messages": [{"role": "user", "content": "Hello"}],
        }
    )

    async def complete_request():
        plan = await service.prepare_completion(request)
        return await service.complete(plan)

    response = asyncio.run(complete_request())

    assert response.object == "chat.completion"
    assert response.choices[0].message.content == "Hello!"
    assert response.usage is not None
    assert response.usage.total_tokens == 12


def test_stream_completion_returns_error_event_on_ollama_timeout() -> None:
    service = ChatCompletionService(
        document_service=cast("DocumentService", FakeDocumentService()),
        llm_model_service=cast("LlmModelService", FakeLlmModelService()),
        chat_client=cast("OllamaChatClient", FakeTimeoutOllamaChatClient()),
    )
    request = ChatCompletionRequest.model_validate(
        {
            "model": "rag-assistant-lite",
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": True,
        }
    )

    async def collect_events() -> list[str]:
        plan = await service.prepare_completion(request)
        return [event async for event in service.stream_completion(plan)]

    events = asyncio.run(collect_events())

    assert any('"code": "ollama_timeout"' in event for event in events)
    assert events[-1] == "data: [DONE]\n\n"


def test_complete_raises_controlled_error_on_ollama_timeout() -> None:
    service = ChatCompletionService(
        document_service=cast("DocumentService", FakeDocumentService()),
        llm_model_service=cast("LlmModelService", FakeLlmModelService()),
        chat_client=cast("OllamaChatClient", FakeTimeoutOllamaChatClient()),
    )
    request = ChatCompletionRequest.model_validate(
        {
            "model": "rag-assistant-lite",
            "messages": [{"role": "user", "content": "Hello"}],
        }
    )

    async def complete_request() -> None:
        plan = await service.prepare_completion(request)
        await service.complete(plan)

    try:
        asyncio.run(complete_request())
    except ChatCompletionTimeoutError as exc:
        assert str(exc) == "Ollama request timed out"
    else:
        raise AssertionError("Expected ChatCompletionTimeoutError")
