import asyncio
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, StreamingResponse

from rag_service.chats.dependencies import ChatCompletionRequestLogServiceDep
from rag_service.chats.models import ChatCompletionRequestStatus
from rag_service.documents.dependencies import DocumentServiceDep
from rag_service.exceptions import BadRequestError, NotFoundError
from rag_service.exceptions.responses import (
    auth_responses,
    internal_server_error_response,
    validation_error_response,
)
from rag_service.llm_models.dependencies import LlmModelServiceDep
from rag_service.redis.rate_limiter import is_rate_limited
from rag_service.security.dependencies import AdminApiKeyDep, UserApiKeyDep
from rag_service.utils import is_dev_env

from .schema import (
    ChatCompletionRequest,
    ChatCompletionRequestLog,
    ChatCompletionRequestLogsList,
    ChatCompletionResponse,
    OpenAIError,
    OpenAIErrorResponse,
)
from .services import ChatCompletionService, ChatCompletionTimeoutError

router = APIRouter(tags=["Chat Completions"])


@router.post(
    path="/chat/completions",
    description="Create an OpenAI-compatible chat completion",
    response_model=None,
    responses={
        200: {
            "description": "Returns a chat completion or SSE stream",
        },
        **auth_responses,
        400: {"model": OpenAIErrorResponse, "description": "Invalid request"},
        404: {"model": OpenAIErrorResponse, "description": "Model not found"},
        429: {"model": OpenAIErrorResponse, "description": "Rate limit exceeded"},
        503: {"model": OpenAIErrorResponse, "description": "LLM provider timeout"},
        **validation_error_response,
        **internal_server_error_response,
    },
)
async def create_chat_completion(
    chat_request: ChatCompletionRequest,
    auth_context: UserApiKeyDep,
    document_service: DocumentServiceDep,
    llm_model_service: LlmModelServiceDep,
    request_log_service: ChatCompletionRequestLogServiceDep,
) -> ChatCompletionResponse | StreamingResponse | JSONResponse:
    if await is_rate_limited(auth_context.user_id, auth_context.requests_per_minute):
        return openai_error_response(
            status_code=429,
            message="Rate limit exceeded. Please slow down your requests.",
            error_type="rate_limit_error",
            code="rate_limit_exceeded",
        )

    service = ChatCompletionService(
        document_service=document_service,
        llm_model_service=llm_model_service,
    )
    request_log = await request_log_service.create_pending(
        user_id=auth_context.user_id,
        api_key_id=auth_context.api_key_id,
        chat_request=chat_request,
    )

    try:
        plan = await service.prepare_completion(chat_request)
        await request_log_service.mark_prepared(request_log=request_log, plan=plan)
    except BadRequestError as exc:
        await request_log_service.finish_failed(
            request_log=request_log,
            error_code=exc.code,
            error_message=exc.detail,
        )
        return openai_error_response(
            status_code=400,
            message=exc.detail,
            error_type="invalid_request_error",
            code=exc.code,
        )
    except NotFoundError as exc:
        await request_log_service.finish_failed(
            request_log=request_log,
            error_code="model_not_found",
            error_message=exc.detail,
        )
        return openai_error_response(
            status_code=404,
            message=exc.detail,
            error_type="invalid_request_error",
            code="model_not_found",
        )

    if chat_request.stream:

        async def mark_stream_succeeded(metrics) -> None:
            await request_log_service.finish_succeeded(
                request_log=request_log,
                plan=plan,
                metrics=metrics,
            )

        async def mark_stream_timeout(metrics) -> None:
            await request_log_service.finish_failed(
                request_log=request_log,
                plan=plan,
                metrics=metrics,
                error_code="provider_timeout",
                error_message="LLM request timed out",
            )

        async def completion_stream():
            try:
                async for event in service.stream_completion(
                    plan,
                    on_complete=mark_stream_succeeded,
                    on_timeout=mark_stream_timeout,
                ):
                    yield event
            except asyncio.CancelledError:
                await request_log_service.finish_interrupted(
                    request_log=request_log,
                    plan=plan,
                )
                raise
            except Exception as exc:
                await request_log_service.finish_failed(
                    request_log=request_log,
                    plan=plan,
                    error_code="chat_completion_failed",
                    error_message=str(exc),
                )
                raise

        return StreamingResponse(
            completion_stream(),
            media_type="text/event-stream",
        )

    try:
        result = await service.complete(plan)
        await request_log_service.finish_succeeded(
            request_log=request_log,
            plan=plan,
            metrics=result.metrics,
        )
        return result.response
    except ChatCompletionTimeoutError as exc:
        await request_log_service.finish_failed(
            request_log=request_log,
            plan=plan,
            error_code="provider_timeout",
            error_message=str(exc),
        )
        return openai_error_response(
            status_code=503,
            message=str(exc),
            error_type="server_error",
            code="provider_timeout",
        )
    except Exception as exc:
        await request_log_service.finish_failed(
            request_log=request_log,
            plan=plan,
            error_code="chat_completion_failed",
            error_message=str(exc),
        )
        raise


@router.get(
    path="/chat-completion-requests",
    description="Get chat completion request usage logs",
    include_in_schema=is_dev_env(),
    responses={
        200: {
            "description": "Returns chat completion request usage logs",
        },
        **auth_responses,
        **internal_server_error_response,
    },
)
async def get_chat_completion_requests(
    admin_context: AdminApiKeyDep,
    request_log_service: ChatCompletionRequestLogServiceDep,
    user_id: UUID | None = None,
    api_key_id: UUID | None = None,
    model: str | None = None,
    status: ChatCompletionRequestStatus | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> ChatCompletionRequestLogsList:
    request_logs, total = await request_log_service.list_requests(
        user_id=user_id,
        api_key_id=api_key_id,
        model=model,
        status=status,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
    return ChatCompletionRequestLogsList(
        requests=[
            ChatCompletionRequestLog.model_validate(request_log) for request_log in request_logs
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


def openai_error_response(
    status_code: int,
    message: str,
    error_type: str,
    code: str,
) -> JSONResponse:
    """
    Return an OpenAI-compatible error response.
    """
    error = OpenAIErrorResponse(
        error=OpenAIError(
            message=message,
            type=error_type,
            code=code,
        )
    )
    return JSONResponse(status_code=status_code, content=error.model_dump())
