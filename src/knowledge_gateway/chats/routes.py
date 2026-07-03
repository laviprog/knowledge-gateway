from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, StreamingResponse

from knowledge_gateway.chats.dependencies import ChatCompletionRequestLogServiceDep
from knowledge_gateway.chats.models import ChatCompletionRequestStatus
from knowledge_gateway.documents.dependencies import DocumentServiceDep
from knowledge_gateway.exceptions.responses import (
    auth_responses,
    internal_server_error_response,
    validation_error_response,
)
from knowledge_gateway.knowledge_bases.dependencies import KnowledgeBaseServiceDep
from knowledge_gateway.llm_models.dependencies import LlmModelServiceDep
from knowledge_gateway.redis.rate_limiter import is_rate_limited
from knowledge_gateway.security.dependencies import AdminDep, UserApiKeyDep
from knowledge_gateway.utils import is_dev_env

from .orchestrator import ChatCompletionError, ChatCompletionOrchestrator
from .schema import (
    ChatCompletionRequest,
    ChatCompletionRequestLog,
    ChatCompletionRequestLogsList,
    ChatCompletionResponse,
    ChatCompletionStats,
    OpenAIError,
    OpenAIErrorResponse,
)
from .services import ChatCompletionService

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
    knowledge_base_service: KnowledgeBaseServiceDep,
    request_log_service: ChatCompletionRequestLogServiceDep,
) -> ChatCompletionResponse | StreamingResponse | JSONResponse:
    if await is_rate_limited(auth_context.user_id, auth_context.requests_per_minute):
        return openai_error_response(
            status_code=429,
            message="Rate limit exceeded. Please slow down your requests.",
            error_type="rate_limit_error",
            code="rate_limit_exceeded",
        )

    orchestrator = ChatCompletionOrchestrator(
        completion_service=ChatCompletionService(
            document_service=document_service,
            llm_model_service=llm_model_service,
            knowledge_base_service=knowledge_base_service,
        ),
        request_log_service=request_log_service,
    )

    prepared = await orchestrator.prepare(
        user_id=auth_context.user_id,
        api_key_id=auth_context.api_key_id,
        chat_request=chat_request,
    )
    if isinstance(prepared, ChatCompletionError):
        return error_to_response(prepared)

    if chat_request.stream:
        return StreamingResponse(
            orchestrator.stream(prepared),
            media_type="text/event-stream",
            headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
        )

    completed = await orchestrator.complete(prepared)
    if isinstance(completed, ChatCompletionError):
        return error_to_response(completed)

    return completed


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
    admin_context: AdminDep,
    request_log_service: ChatCompletionRequestLogServiceDep,
    user_id: UUID | None = None,
    api_key_id: UUID | None = None,
    model: str | None = None,
    knowledge_base_id: UUID | None = None,
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
        knowledge_base_id=knowledge_base_id,
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


@router.get(
    path="/chat-completion-requests/stats",
    description="Get aggregated chat completion usage statistics",
    include_in_schema=is_dev_env(),
    responses={
        200: {
            "description": "Returns aggregated usage statistics",
        },
        **auth_responses,
        **internal_server_error_response,
    },
)
async def get_chat_completion_stats(
    admin_context: AdminDep,
    request_log_service: ChatCompletionRequestLogServiceDep,
    user_id: UUID | None = None,
    api_key_id: UUID | None = None,
    model: str | None = None,
    knowledge_base_id: UUID | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> ChatCompletionStats:
    return await request_log_service.get_stats(
        user_id=user_id,
        api_key_id=api_key_id,
        model=model,
        knowledge_base_id=knowledge_base_id,
        date_from=date_from,
        date_to=date_to,
    )


def error_to_response(error: ChatCompletionError) -> JSONResponse:
    """
    Map a `ChatCompletionError` to an OpenAI-compatible error response.
    """
    return openai_error_response(
        status_code=error.status_code,
        message=error.message,
        error_type=error.error_type,
        code=error.code,
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
