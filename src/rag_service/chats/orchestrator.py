import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass
from uuid import UUID

from rag_service.exceptions import BadRequestError, NotFoundError
from rag_service.llm.base import ProviderTimeoutError
from rag_service.log_config import get_log

from .schema import ChatCompletionRequest, ChatCompletionResponse
from .services import (
    ChatCompletionMetrics,
    ChatCompletionPlan,
    ChatCompletionRequestLogService,
    ChatCompletionService,
    ChatCompletionTimeoutError,
)

log = get_log(__name__)


@dataclass(frozen=True)
class ChatCompletionError:
    """
    Transport-agnostic chat completion error, mapped to an OpenAI error envelope by the route.
    """

    status_code: int
    message: str
    error_type: str
    code: str


class ChatCompletionOrchestrator:
    """
    Owns the chat completion request lifecycle: usage-log bookkeeping around preparation,
    streaming, and non-streaming generation. Keeps the route thin and framework-agnostic.
    """

    def __init__(
        self,
        completion_service: ChatCompletionService,
        request_log_service: ChatCompletionRequestLogService,
    ) -> None:
        self.completion_service = completion_service
        self.request_log_service = request_log_service
        self._request_log = None

    async def prepare(
        self,
        *,
        user_id: UUID,
        api_key_id: UUID,
        chat_request: ChatCompletionRequest,
    ) -> ChatCompletionPlan | ChatCompletionError:
        """
        Write a pending usage-log row and build the completion plan, mapping known
        failures to a `ChatCompletionError`.
        """
        self._request_log = await self.request_log_service.create_pending(
            user_id=user_id,
            api_key_id=api_key_id,
            chat_request=chat_request,
        )

        try:
            plan = await self.completion_service.prepare_completion(chat_request)
        except BadRequestError as exc:
            await self.request_log_service.finish_failed(
                request_log=self._request_log,
                error_code=exc.code,
                error_message=exc.detail,
            )
            return ChatCompletionError(400, exc.detail, "invalid_request_error", exc.code)
        except NotFoundError as exc:
            await self.request_log_service.finish_failed(
                request_log=self._request_log,
                error_code="model_not_found",
                error_message=exc.detail,
            )
            return ChatCompletionError(404, exc.detail, "invalid_request_error", "model_not_found")
        except ProviderTimeoutError as exc:
            # Embedding call to the LLM provider failed during retrieval.
            await self.request_log_service.finish_failed(
                request_log=self._request_log,
                error_code="provider_timeout",
                error_message=str(exc),
            )
            return ChatCompletionError(503, str(exc), "server_error", "provider_timeout")
        except Exception as exc:
            # Any other preparation failure (e.g. Qdrant) must still finalize the log row,
            # otherwise it stays PENDING forever and skews usage analytics.
            await self.request_log_service.finish_failed(
                request_log=self._request_log,
                error_code="preparation_failed",
                error_message=str(exc),
            )
            raise

        await self.request_log_service.mark_prepared(request_log=self._request_log, plan=plan)
        return plan

    async def stream(self, plan: ChatCompletionPlan) -> AsyncIterator[str]:
        """
        Stream SSE events, finalizing the usage-log row on completion, timeout,
        client disconnect, or failure.
        """
        request_log = self._require_request_log()

        async def on_complete(metrics: ChatCompletionMetrics) -> None:
            await self.request_log_service.finish_succeeded(
                request_log=request_log,
                plan=plan,
                metrics=metrics,
            )

        async def on_timeout(metrics: ChatCompletionMetrics) -> None:
            await self.request_log_service.finish_failed(
                request_log=request_log,
                plan=plan,
                metrics=metrics,
                error_code="provider_timeout",
                error_message="LLM request timed out",
            )

        try:
            async for event in self.completion_service.stream_completion(
                plan,
                on_complete=on_complete,
                on_timeout=on_timeout,
            ):
                yield event
        except asyncio.CancelledError:
            log.info(
                "Chat completion stream interrupted by client", completion_id=plan.completion_id
            )
            await self.request_log_service.finish_interrupted(request_log=request_log, plan=plan)
            raise
        except Exception as exc:
            await self.request_log_service.finish_failed(
                request_log=request_log,
                plan=plan,
                error_code="chat_completion_failed",
                error_message=str(exc),
            )
            raise

    async def complete(
        self,
        plan: ChatCompletionPlan,
    ) -> ChatCompletionResponse | ChatCompletionError:
        """
        Run a non-streaming completion, finalizing the usage-log row.
        """
        request_log = self._require_request_log()

        try:
            result = await self.completion_service.complete(plan)
        except ChatCompletionTimeoutError as exc:
            await self.request_log_service.finish_failed(
                request_log=request_log,
                plan=plan,
                error_code="provider_timeout",
                error_message=str(exc),
            )
            return ChatCompletionError(503, str(exc), "server_error", "provider_timeout")
        except Exception as exc:
            await self.request_log_service.finish_failed(
                request_log=request_log,
                plan=plan,
                error_code="chat_completion_failed",
                error_message=str(exc),
            )
            raise

        await self.request_log_service.finish_succeeded(
            request_log=request_log,
            plan=plan,
            metrics=result.metrics,
        )
        return result.response

    def _require_request_log(self):
        if self._request_log is None:
            raise RuntimeError("prepare() must be called before stream()/complete()")
        return self._request_log
