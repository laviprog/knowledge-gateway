import time
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any
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
from rag_service.llm.base import ChatChunk, ChatClient, ProviderTimeoutError
from rag_service.llm.chat import OpenAIChatClient
from rag_service.llm_models.models import LlmModel
from rag_service.llm_models.services import LlmModelService
from rag_service.log_config import get_log
from rag_service.utils import generate_uuid

from .prompts import build_rag_messages, get_latest_user_message
from .schema import (
    ChatCompletionChoice,
    ChatCompletionMessage,
    ChatCompletionModelStats,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionStats,
    ChatCompletionStatusCount,
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
    messages: list[dict[str, str]]
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
    llm_ttfb_ms: float | None
    llm_generation_ms: float | None
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
        chat_client: ChatClient | None = None,
    ) -> None:
        self.document_service = document_service
        self.llm_model_service = llm_model_service
        self.chat_client = chat_client or OpenAIChatClient()

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
        messages = build_rag_messages(chat_request.messages, retrieval.results)

        log.info(
            "RAG retrieval completed",
            model=chat_request.model,
            provider_model=llm_model.provider_model,
            chunks_count=len(retrieval.results),
            document_ids=sorted({result.document_id for result in retrieval.results}),
            embedding_ms=retrieval.timings.embedding_ms,
            qdrant_search_ms=retrieval.timings.qdrant_search_ms,
            retrieval_total_ms=retrieval.timings.total_ms,
        )

        return ChatCompletionPlan(
            completion_id=f"chatcmpl-{generate_uuid()}",
            created=int(time.time()),
            request=chat_request,
            llm_model=llm_model,
            messages=messages,
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
            async for chunk in self.iter_chunks(plan):
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
        except ProviderTimeoutError:
            metrics = self.log_timeout(plan=plan)
            if on_timeout is not None:
                await on_timeout(metrics)

            yield format_sse_event(
                {
                    "error": {
                        "message": "LLM request timed out",
                        "type": "server_error",
                        "code": "provider_timeout",
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
            async for chunk in self.iter_chunks(plan):
                if chunk.prompt_tokens is not None:
                    prompt_tokens = chunk.prompt_tokens

                if chunk.completion_tokens is not None:
                    completion_tokens = chunk.completion_tokens

                if not chunk.content:
                    continue

                if first_token_ms is None:
                    first_token_ms = round((time.perf_counter() - generation_start) * 1000, 2)

                content_parts.append(chunk.content)
        except ProviderTimeoutError as exc:
            self.log_timeout(plan=plan)
            raise ChatCompletionTimeoutError("LLM request timed out") from exc
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

    async def iter_chunks(
        self,
        plan: ChatCompletionPlan,
    ) -> AsyncIterator[ChatChunk]:
        """
        Stream chunks from the LLM provider.
        """
        max_completion_tokens = (
            plan.request.max_completion_tokens or plan.llm_model.max_completion_tokens
        )
        async for chunk in self.chat_client.stream_chat(
            model=plan.llm_model.provider_model,
            messages=plan.messages,
            temperature=plan.request.temperature,
            top_p=plan.request.top_p,
            max_completion_tokens=max_completion_tokens,
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
            llm_ttfb_ms=first_token_ms,
            llm_generation_ms=round((time.perf_counter() - generation_start) * 1000, 2),
            total_ms=round((time.perf_counter() - plan.started_at) * 1000, 2),
        )

        log.info(
            "Chat completion completed",
            model=plan.request.model,
            provider_model=plan.llm_model.provider_model,
            chunks_count=len(plan.retrieval.results),
            embedding_ms=plan.retrieval.timings.embedding_ms,
            qdrant_search_ms=plan.retrieval.timings.qdrant_search_ms,
            retrieval_total_ms=plan.retrieval.timings.total_ms,
            llm_ttfb_ms=metrics.llm_ttfb_ms,
            llm_generation_ms=metrics.llm_generation_ms,
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
            llm_ttfb_ms=None,
            llm_generation_ms=None,
            total_ms=round((time.perf_counter() - plan.started_at) * 1000, 2),
        )

        log.warning(
            "Chat completion timed out",
            model=plan.request.model,
            provider_model=plan.llm_model.provider_model,
            timeout_seconds=settings.LLM_TIMEOUT_SECONDS,
            chunks_count=len(plan.retrieval.results),
            embedding_ms=plan.retrieval.timings.embedding_ms,
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
        filters = self._build_filters(
            user_id=user_id,
            api_key_id=api_key_id,
            model=model,
            status=status,
            date_from=date_from,
            date_to=date_to,
        )

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

    async def get_stats(
        self,
        *,
        user_id: UUID | None = None,
        api_key_id: UUID | None = None,
        model: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> ChatCompletionStats:
        """
        Aggregate usage metrics (totals, token sums/averages, latency averages) over the
        filtered usage-log rows, plus a per-model breakdown.
        """
        model_cls = ChatCompletionRequestLogModel
        filters = self._build_filters(
            user_id=user_id,
            api_key_id=api_key_id,
            model=model,
            status=None,
            date_from=date_from,
            date_to=date_to,
        )
        session = self.repository.session

        totals_statement = select(
            func.count(),
            func.sum(model_cls.prompt_tokens),
            func.sum(model_cls.completion_tokens),
            func.sum(model_cls.total_tokens),
            func.avg(model_cls.embedding_ms),
            func.avg(model_cls.llm_ttfb_ms),
            func.avg(model_cls.llm_generation_ms),
            func.avg(model_cls.total_ms),
        ).where(*filters)
        totals_row = (await session.execute(totals_statement)).one()

        status_statement = (
            select(model_cls.status, func.count()).where(*filters).group_by(model_cls.status)
        )
        status_rows = (await session.execute(status_statement)).all()

        model_statement = (
            select(
                model_cls.model_public_id,
                func.count(),
                func.sum(model_cls.total_tokens),
                func.avg(model_cls.total_ms),
            )
            .where(*filters)
            .group_by(model_cls.model_public_id)
            .order_by(func.count().desc())
        )
        model_rows = (await session.execute(model_statement)).all()

        return ChatCompletionStats(
            total_requests=totals_row[0],
            by_status=[
                ChatCompletionStatusCount(status=status, count=count)
                for status, count in status_rows
            ],
            prompt_tokens_total=_as_int(totals_row[1]),
            completion_tokens_total=_as_int(totals_row[2]),
            total_tokens_total=_as_int(totals_row[3]),
            avg_embedding_ms=_round_or_none(totals_row[4]),
            avg_llm_ttfb_ms=_round_or_none(totals_row[5]),
            avg_llm_generation_ms=_round_or_none(totals_row[6]),
            avg_total_ms=_round_or_none(totals_row[7]),
            by_model=[
                ChatCompletionModelStats(
                    model_public_id=model_public_id,
                    requests=requests,
                    total_tokens=_as_int(total_tokens),
                    avg_total_ms=_round_or_none(avg_total_ms),
                )
                for model_public_id, requests, total_tokens, avg_total_ms in model_rows
            ],
        )

    @staticmethod
    def _build_filters(
        *,
        user_id: UUID | None,
        api_key_id: UUID | None,
        model: str | None,
        status: ChatCompletionRequestStatus | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> "list[ColumnElement[bool]]":
        """
        Build shared WHERE clauses for usage-log queries.
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
        return filters

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
        request_log.embedding_ms = plan.retrieval.timings.embedding_ms
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
        request_log.llm_ttfb_ms = metrics.llm_ttfb_ms
        request_log.llm_generation_ms = metrics.llm_generation_ms
        request_log.total_ms = metrics.total_ms


def get_query_length(chat_request: ChatCompletionRequest) -> int | None:
    """
    Return latest non-empty user message length without storing message content.
    """
    for message in reversed(chat_request.messages):
        if message.role == "user" and message.content.strip():
            return len(message.content)

    return None


def _as_int(value: Any) -> int | None:
    """
    Coerce a SQL aggregate (which may be Decimal/None) to an int.
    """
    return int(value) if value is not None else None


def _round_or_none(value: Any) -> float | None:
    """
    Coerce a SQL average (which may be Decimal/None) to a rounded float.
    """
    return round(float(value), 2) if value is not None else None
