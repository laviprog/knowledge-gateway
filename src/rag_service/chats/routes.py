from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse

from rag_service.documents.dependencies import DocumentServiceDep
from rag_service.exceptions import BadRequestError, NotFoundError
from rag_service.exceptions.responses import (
    auth_responses,
    internal_server_error_response,
    validation_error_response,
)
from rag_service.llm_models.dependencies import LlmModelServiceDep
from rag_service.security.dependencies import UserApiKeyDep

from .schema import (
    ChatCompletionRequest,
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
        503: {"model": OpenAIErrorResponse, "description": "LLM provider timeout"},
        **validation_error_response,
        **internal_server_error_response,
    },
)
async def create_chat_completion(
    chat_request: ChatCompletionRequest,
    user_id: UserApiKeyDep,
    document_service: DocumentServiceDep,
    llm_model_service: LlmModelServiceDep,
) -> ChatCompletionResponse | StreamingResponse | JSONResponse:
    service = ChatCompletionService(
        document_service=document_service,
        llm_model_service=llm_model_service,
    )

    try:
        plan = await service.prepare_completion(chat_request)
    except BadRequestError as exc:
        return openai_error_response(
            status_code=400,
            message=exc.detail,
            error_type="invalid_request_error",
            code=exc.code,
        )
    except NotFoundError as exc:
        return openai_error_response(
            status_code=404,
            message=exc.detail,
            error_type="invalid_request_error",
            code="model_not_found",
        )

    if chat_request.stream:
        return StreamingResponse(
            service.stream_completion(plan),
            media_type="text/event-stream",
        )

    try:
        return await service.complete(plan)
    except ChatCompletionTimeoutError as exc:
        return openai_error_response(
            status_code=503,
            message=str(exc),
            error_type="server_error",
            code="ollama_timeout",
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
