import time
from collections.abc import AsyncIterator
from dataclasses import dataclass

from rag_service.config import settings
from rag_service.documents.services import DocumentSearchWithMetrics, DocumentService
from rag_service.llm_models.models import LlmModel
from rag_service.llm_models.services import LlmModelService
from rag_service.log_config import get_log
from rag_service.ollama.chat import OllamaChatChunk, OllamaChatClient
from rag_service.utils import generate_uuid

from .prompts import build_rag_messages, get_latest_user_message
from .schema import (
    ChatCompletionChoice,
    ChatCompletionMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionUsage,
)
from .sse import build_chunk, build_usage_chunk, format_sse_event

log = get_log(__name__)


@dataclass(frozen=True)
class ChatCompletionPlan:
    """
    Prepared chat completion plan.
    """

    completion_id: str
    created: int
    request: ChatCompletionRequest
    llm_model: LlmModel
    ollama_messages: list[dict[str, str]]
    retrieval: DocumentSearchWithMetrics
    started_at: float


class ChatCompletionService:
    """
    OpenAI-compatible chat completion service.
    """

    def __init__(
        self,
        document_service: DocumentService,
        llm_model_service: LlmModelService,
        chat_client: OllamaChatClient | None = None,
    ) -> None:
        self.document_service = document_service
        self.llm_model_service = llm_model_service
        self.chat_client = chat_client or OllamaChatClient()

    async def prepare_completion(
        self,
        chat_request: ChatCompletionRequest,
    ) -> ChatCompletionPlan:
        """
        Prepare model, retrieval context, and prompt.
        """
        started_at = time.perf_counter()
        llm_model = await self.llm_model_service.get_by_public_id_or_raise(chat_request.model)

        log.info(
            "Chat completion started",
            model=chat_request.model,
            provider_model=llm_model.provider_model,
            messages_count=len(chat_request.messages),
            stream=chat_request.stream,
        )

        query = get_latest_user_message(chat_request.messages)
        retrieval = await self.document_service.search_documents_with_metrics(
            query=query,
            limit=settings.RAG_RETRIEVAL_LIMIT,
        )
        ollama_messages = build_rag_messages(chat_request.messages, retrieval.results)

        log.info(
            "RAG retrieval completed",
            model=chat_request.model,
            provider_model=llm_model.provider_model,
            chunks_count=len(retrieval.results),
            document_ids=sorted({result.document_id for result in retrieval.results}),
            ollama_embedding_ms=retrieval.timings.ollama_embedding_ms,
            qdrant_search_ms=retrieval.timings.qdrant_search_ms,
            retrieval_total_ms=retrieval.timings.total_ms,
        )

        return ChatCompletionPlan(
            completion_id=f"chatcmpl-{generate_uuid()}",
            created=int(time.time()),
            request=chat_request,
            llm_model=llm_model,
            ollama_messages=ollama_messages,
            retrieval=retrieval,
            started_at=started_at,
        )

    async def stream_completion(self, plan: ChatCompletionPlan) -> AsyncIterator[str]:
        """
        Stream an OpenAI-compatible chat completion.
        """
        generation_start = time.perf_counter()
        first_token_ms: float | None = None
        prompt_tokens: int | None = None
        completion_tokens: int | None = None

        yield format_sse_event(
            build_chunk(
                completion_id=plan.completion_id,
                created=plan.created,
                model=plan.request.model,
                delta={"role": "assistant"},
            )
        )

        try:
            async for chunk in self.iter_ollama_chunks(plan):
                if chunk.prompt_tokens is not None:
                    prompt_tokens = chunk.prompt_tokens

                if chunk.completion_tokens is not None:
                    completion_tokens = chunk.completion_tokens

                if not chunk.content:
                    continue

                if first_token_ms is None:
                    first_token_ms = round((time.perf_counter() - generation_start) * 1000, 2)

                yield format_sse_event(
                    build_chunk(
                        completion_id=plan.completion_id,
                        created=plan.created,
                        model=plan.request.model,
                        delta={"content": chunk.content},
                    )
                )

            yield format_sse_event(
                build_chunk(
                    completion_id=plan.completion_id,
                    created=plan.created,
                    model=plan.request.model,
                    delta={},
                    finish_reason="stop",
                )
            )

            if (
                plan.request.stream_options is not None
                and plan.request.stream_options.include_usage
                and prompt_tokens is not None
                and completion_tokens is not None
            ):
                yield format_sse_event(
                    build_usage_chunk(
                        completion_id=plan.completion_id,
                        created=plan.created,
                        model=plan.request.model,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                    )
                )

            yield format_sse_event("[DONE]")
            self.log_completed(
                plan=plan,
                generation_start=generation_start,
                first_token_ms=first_token_ms,
            )
        except Exception:
            log.exception(
                "Chat completion failed",
                model=plan.request.model,
                provider_model=plan.llm_model.provider_model,
                total_ms=round((time.perf_counter() - plan.started_at) * 1000, 2),
            )
            raise

    async def complete(self, plan: ChatCompletionPlan) -> ChatCompletionResponse:
        """
        Create a non-streaming OpenAI-compatible chat completion.
        """
        generation_start = time.perf_counter()
        first_token_ms: float | None = None
        prompt_tokens: int | None = None
        completion_tokens: int | None = None
        content_parts: list[str] = []

        try:
            async for chunk in self.iter_ollama_chunks(plan):
                if chunk.prompt_tokens is not None:
                    prompt_tokens = chunk.prompt_tokens

                if chunk.completion_tokens is not None:
                    completion_tokens = chunk.completion_tokens

                if not chunk.content:
                    continue

                if first_token_ms is None:
                    first_token_ms = round((time.perf_counter() - generation_start) * 1000, 2)

                content_parts.append(chunk.content)
        except Exception:
            log.exception(
                "Chat completion failed",
                model=plan.request.model,
                provider_model=plan.llm_model.provider_model,
                total_ms=round((time.perf_counter() - plan.started_at) * 1000, 2),
            )
            raise

        self.log_completed(
            plan=plan,
            generation_start=generation_start,
            first_token_ms=first_token_ms,
        )

        usage = None
        if prompt_tokens is not None and completion_tokens is not None:
            usage = ChatCompletionUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            )

        return ChatCompletionResponse(
            id=plan.completion_id,
            created=plan.created,
            model=plan.request.model,
            choices=[
                ChatCompletionChoice(
                    message=ChatCompletionMessage(content="".join(content_parts)),
                )
            ],
            usage=usage,
        )

    async def iter_ollama_chunks(
        self,
        plan: ChatCompletionPlan,
    ) -> AsyncIterator[OllamaChatChunk]:
        """
        Stream chunks from Ollama.
        """
        max_completion_tokens = (
            plan.request.max_completion_tokens or plan.llm_model.max_completion_tokens
        )
        async for chunk in self.chat_client.stream_chat(
            model=plan.llm_model.provider_model,
            messages=plan.ollama_messages,
            temperature=plan.request.temperature,
            top_p=plan.request.top_p,
            max_completion_tokens=max_completion_tokens,
            think=plan.request.think,
        ):
            yield chunk

    def log_completed(
        self,
        plan: ChatCompletionPlan,
        generation_start: float,
        first_token_ms: float | None,
    ) -> None:
        """
        Log chat completion metrics.
        """
        log.info(
            "Chat completion completed",
            model=plan.request.model,
            provider_model=plan.llm_model.provider_model,
            chunks_count=len(plan.retrieval.results),
            ollama_embedding_ms=plan.retrieval.timings.ollama_embedding_ms,
            qdrant_search_ms=plan.retrieval.timings.qdrant_search_ms,
            retrieval_total_ms=plan.retrieval.timings.total_ms,
            ollama_ttfb_ms=first_token_ms,
            ollama_generation_ms=round((time.perf_counter() - generation_start) * 1000, 2),
            total_ms=round((time.perf_counter() - plan.started_at) * 1000, 2),
        )
