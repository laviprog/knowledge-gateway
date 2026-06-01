import time
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy import func, select

from rag_service.chats.models import (
    ChatCompletionRequestLogModel,
    ChatCompletionRequestStatus,
)
from rag_service.chats.repositories import ChatCompletionRequestLogRepository
from rag_service.config import settings
from rag_service.documents.services import DocumentSearchWithMetrics, DocumentService
from rag_service.llm_models.models import LlmModel
from rag_service.llm_models.services import LlmModelService
from rag_service.log_config import get_log
from rag_service.ollama.chat import OllamaChatChunk, OllamaChatClient, OllamaTimeoutError
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

if TYPE_CHECKING:
    from sqlalchemy.sql.elements import ColumnElement


class ChatCompletionTimeoutError(Exception):
    """
    Raised when chat completion generation times out.
    """


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


@dataclass(frozen=True)
class ChatCompletionMetrics:
    """
    Chat completion token and latency metrics.
    """

    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    ollama_ttfb_ms: float | None
    ollama_generation_ms: float | None
    total_ms: float


@dataclass(frozen=True)
class ChatCompletionResult:
    """
    Non-streaming chat completion response with metrics.
    """

    response: ChatCompletionResponse
    metrics: ChatCompletionMetrics


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

    async def stream_completion(
        self,
        plan: ChatCompletionPlan,
        on_complete: Callable[[ChatCompletionMetrics], Awaitable[None]] | None = None,
        on_timeout: Callable[[ChatCompletionMetrics], Awaitable[None]] | None = None,
    ) -> AsyncIterator[str]:
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

            metrics = self.log_completed(
                plan=plan,
                generation_start=generation_start,
                first_token_ms=first_token_ms,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )
            if on_complete is not None:
                await on_complete(metrics)

            yield format_sse_event("[DONE]")
        except OllamaTimeoutError:
            metrics = self.log_timeout(plan=plan)
            if on_timeout is not None:
                await on_timeout(metrics)

            yield format_sse_event(
                {
                    "error": {
                        "message": "Ollama request timed out",
                        "type": "server_error",
                        "code": "ollama_timeout",
                    }
                }
            )
            yield format_sse_event("[DONE]")
        except Exception:
            log.exception(
                "Chat completion failed",
                model=plan.request.model,
                provider_model=plan.llm_model.provider_model,
                total_ms=round((time.perf_counter() - plan.started_at) * 1000, 2),
            )
            raise

    async def complete(self, plan: ChatCompletionPlan) -> ChatCompletionResult:
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
        except OllamaTimeoutError as exc:
            self.log_timeout(plan=plan)
            raise ChatCompletionTimeoutError("Ollama request timed out") from exc
        except Exception:
            log.exception(
                "Chat completion failed",
                model=plan.request.model,
                provider_model=plan.llm_model.provider_model,
                total_ms=round((time.perf_counter() - plan.started_at) * 1000, 2),
            )
            raise

        metrics = self.log_completed(
            plan=plan,
            generation_start=generation_start,
            first_token_ms=first_token_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

        usage = None
        if prompt_tokens is not None and completion_tokens is not None:
            usage = ChatCompletionUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            )

        return ChatCompletionResult(
            response=ChatCompletionResponse(
                id=plan.completion_id,
                created=plan.created,
                model=plan.request.model,
                choices=[
                    ChatCompletionChoice(
                        message=ChatCompletionMessage(content="".join(content_parts)),
                    )
                ],
                usage=usage,
            ),
            metrics=metrics,
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
        prompt_tokens: int | None,
        completion_tokens: int | None,
    ) -> ChatCompletionMetrics:
        """
        Log chat completion metrics.
        """
        metrics = ChatCompletionMetrics(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=(
                prompt_tokens + completion_tokens
                if prompt_tokens is not None and completion_tokens is not None
                else None
            ),
            ollama_ttfb_ms=first_token_ms,
            ollama_generation_ms=round((time.perf_counter() - generation_start) * 1000, 2),
            total_ms=round((time.perf_counter() - plan.started_at) * 1000, 2),
        )

        log.info(
            "Chat completion completed",
            model=plan.request.model,
            provider_model=plan.llm_model.provider_model,
            chunks_count=len(plan.retrieval.results),
            ollama_embedding_ms=plan.retrieval.timings.ollama_embedding_ms,
            qdrant_search_ms=plan.retrieval.timings.qdrant_search_ms,
            retrieval_total_ms=plan.retrieval.timings.total_ms,
            ollama_ttfb_ms=metrics.ollama_ttfb_ms,
            ollama_generation_ms=metrics.ollama_generation_ms,
            total_ms=metrics.total_ms,
        )

        return metrics

    def log_timeout(self, plan: ChatCompletionPlan) -> ChatCompletionMetrics:
        """
        Log chat completion timeout without traceback.
        """
        metrics = ChatCompletionMetrics(
            prompt_tokens=None,
            completion_tokens=None,
            total_tokens=None,
            ollama_ttfb_ms=None,
            ollama_generation_ms=None,
            total_ms=round((time.perf_counter() - plan.started_at) * 1000, 2),
        )

        log.warning(
            "Chat completion timed out",
            model=plan.request.model,
            provider_model=plan.llm_model.provider_model,
            timeout_seconds=settings.OLLAMA_TIMEOUT_SECONDS,
            chunks_count=len(plan.retrieval.results),
            ollama_embedding_ms=plan.retrieval.timings.ollama_embedding_ms,
            qdrant_search_ms=plan.retrieval.timings.qdrant_search_ms,
            retrieval_total_ms=plan.retrieval.timings.total_ms,
            total_ms=metrics.total_ms,
        )

        return metrics


class ChatCompletionRequestLogService(
    SQLAlchemyAsyncRepositoryService[
        ChatCompletionRequestLogModel,
        ChatCompletionRequestLogRepository,
    ]
):
    """Chat Completion Request Log Service"""

    repository_type = ChatCompletionRequestLogRepository

    async def create_pending(
        self,
        *,
        user_id: UUID,
        api_key_id: UUID,
        chat_request: ChatCompletionRequest,
    ) -> ChatCompletionRequestLogModel:
        """
        Create a pending usage log row before model generation starts.
        """
        request_log = ChatCompletionRequestLogModel(
            user_id=user_id,
            api_key_id=api_key_id,
            model_public_id=chat_request.model,
            request_id=f"chatreq-{generate_uuid()}",
            stream=chat_request.stream,
            status=ChatCompletionRequestStatus.PENDING,
            messages_count=len(chat_request.messages),
            query_length=get_query_length(chat_request),
        )
        return await self.repository.add(request_log, auto_commit=True)

    async def mark_prepared(
        self,
        *,
        request_log: ChatCompletionRequestLogModel,
        plan: ChatCompletionPlan,
    ) -> ChatCompletionRequestLogModel:
        """
        Save model and retrieval details once request preparation succeeds.
        """
        self.apply_plan(request_log, plan)
        return await self.repository.update(request_log, auto_commit=True)

    async def finish_succeeded(
        self,
        *,
        request_log: ChatCompletionRequestLogModel,
        plan: ChatCompletionPlan,
        metrics: ChatCompletionMetrics,
    ) -> ChatCompletionRequestLogModel:
        """
        Mark a chat completion request as succeeded.
        """
        self.apply_plan(request_log, plan)
        self.apply_metrics(request_log, metrics)
        request_log.status = ChatCompletionRequestStatus.SUCCEEDED
        request_log.error_code = None
        request_log.error_message = None
        return await self.repository.update(request_log, auto_commit=True)

    async def finish_failed(
        self,
        *,
        request_log: ChatCompletionRequestLogModel,
        error_code: str,
        error_message: str,
        plan: ChatCompletionPlan | None = None,
        metrics: ChatCompletionMetrics | None = None,
    ) -> ChatCompletionRequestLogModel:
        """
        Mark a chat completion request as failed.
        """
        if plan is not None:
            self.apply_plan(request_log, plan)
        if metrics is not None:
            self.apply_metrics(request_log, metrics)
        elif plan is not None:
            request_log.total_ms = round((time.perf_counter() - plan.started_at) * 1000, 2)

        request_log.status = ChatCompletionRequestStatus.FAILED
        request_log.error_code = error_code
        request_log.error_message = error_message[:1000]
        return await self.repository.update(request_log, auto_commit=True)

    async def finish_interrupted(
        self,
        *,
        request_log: ChatCompletionRequestLogModel,
        plan: ChatCompletionPlan,
    ) -> ChatCompletionRequestLogModel:
        """
        Mark a streaming request as interrupted by the client.
        """
        self.apply_plan(request_log, plan)
        request_log.status = ChatCompletionRequestStatus.INTERRUPTED
        request_log.error_code = "client_disconnected"
        request_log.error_message = "Streaming response was interrupted before completion"
        request_log.total_ms = round((time.perf_counter() - plan.started_at) * 1000, 2)
        return await self.repository.update(request_log, auto_commit=True)

    async def list_requests(
        self,
        *,
        user_id: UUID | None = None,
        api_key_id: UUID | None = None,
        model: str | None = None,
        status: ChatCompletionRequestStatus | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[ChatCompletionRequestLogModel], int]:
        """
        List usage log rows with basic admin filters.
        """
        filters: list[ColumnElement[bool]] = [ChatCompletionRequestLogModel.deleted_at.is_(None)]
        if user_id is not None:
            filters.append(ChatCompletionRequestLogModel.user_id == user_id)
        if api_key_id is not None:
            filters.append(ChatCompletionRequestLogModel.api_key_id == api_key_id)
        if model is not None:
            filters.append(ChatCompletionRequestLogModel.model_public_id == model)
        if status is not None:
            filters.append(ChatCompletionRequestLogModel.status == status)
        if date_from is not None:
            filters.append(ChatCompletionRequestLogModel.created_at >= date_from)
        if date_to is not None:
            filters.append(ChatCompletionRequestLogModel.created_at <= date_to)

        statement = (
            select(ChatCompletionRequestLogModel)
            .where(*filters)
            .order_by(ChatCompletionRequestLogModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        count_statement = (
            select(func.count()).select_from(ChatCompletionRequestLogModel).where(*filters)
        )

        result = await self.repository.session.execute(statement)
        count_result = await self.repository.session.execute(count_statement)
        return list(result.scalars().all()), count_result.scalar_one()

    @staticmethod
    def apply_plan(
        request_log: ChatCompletionRequestLogModel,
        plan: ChatCompletionPlan,
    ) -> None:
        request_log.model_id = plan.llm_model.id
        request_log.model_public_id = plan.llm_model.public_id
        request_log.provider = plan.llm_model.provider
        request_log.provider_model = plan.llm_model.provider_model
        request_log.completion_id = plan.completion_id
        request_log.chunks_count = len(plan.retrieval.results)
        request_log.ollama_embedding_ms = plan.retrieval.timings.ollama_embedding_ms
        request_log.qdrant_search_ms = plan.retrieval.timings.qdrant_search_ms
        request_log.retrieval_total_ms = plan.retrieval.timings.total_ms

    @staticmethod
    def apply_metrics(
        request_log: ChatCompletionRequestLogModel,
        metrics: ChatCompletionMetrics,
    ) -> None:
        request_log.prompt_tokens = metrics.prompt_tokens
        request_log.completion_tokens = metrics.completion_tokens
        request_log.total_tokens = metrics.total_tokens
        request_log.ollama_ttfb_ms = metrics.ollama_ttfb_ms
        request_log.ollama_generation_ms = metrics.ollama_generation_ms
        request_log.total_ms = metrics.total_ms


def get_query_length(chat_request: ChatCompletionRequest) -> int | None:
    """
    Return latest non-empty user message length without storing message content.
    """
    for message in reversed(chat_request.messages):
        if message.role == "user" and message.content.strip():
            return len(message.content)

    return None
