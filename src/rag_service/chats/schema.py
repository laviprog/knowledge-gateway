from datetime import datetime
from typing import Any, ClassVar, Literal
from uuid import UUID

from pydantic import ConfigDict, Field

from rag_service.chats.models import ChatCompletionRequestStatus
from rag_service.schema import BaseSchema

ChatRole = Literal["system", "user", "assistant", "tool"]


class ChatMessage(BaseSchema):
    role: ChatRole
    content: str = ""

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True, extra="ignore")


class ChatCompletionStreamOptions(BaseSchema):
    include_usage: bool = False

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True, extra="ignore")


class ChatCompletionRequest(BaseSchema):
    model: str = Field(min_length=1)
    messages: list[ChatMessage] = Field(min_length=1)
    stream: bool = False
    stream_options: ChatCompletionStreamOptions | None = None
    temperature: float | None = Field(default=None, ge=0, le=2)
    top_p: float | None = Field(default=None, gt=0, le=1)
    max_completion_tokens: int | None = Field(default=None, gt=0)
    # Non-standard extension (clients pass it via OpenAI SDK `extra_body`). Selects the
    # knowledge base for RAG retrieval; when omitted, the request runs without retrieval.
    knowledge_base_id: UUID | None = None

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True, extra="ignore")


class ChatCompletionMessage(BaseSchema):
    role: Literal["assistant"] = "assistant"
    content: str


class ChatCompletionChoice(BaseSchema):
    index: int = 0
    message: ChatCompletionMessage
    finish_reason: str = "stop"


class ChatCompletionUsage(BaseSchema):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseSchema):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatCompletionChoice]
    usage: ChatCompletionUsage | None = None


class OpenAIError(BaseSchema):
    message: str
    type: str
    code: str


class OpenAIErrorResponse(BaseSchema):
    error: OpenAIError


class ChatCompletionRequestLog(BaseSchema):
    id: UUID
    api_key_id: UUID
    user_id: UUID
    model_id: UUID | None
    model_public_id: str
    provider: str | None
    provider_model: str | None
    request_id: str
    completion_id: str | None
    stream: bool
    status: ChatCompletionRequestStatus
    error_code: str | None
    error_message: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    chunks_count: int | None
    retrieval_total_ms: float | None
    embedding_ms: float | None
    qdrant_search_ms: float | None
    llm_ttfb_ms: float | None
    llm_generation_ms: float | None
    total_ms: float | None
    messages_count: int | None
    query_length: int | None
    created_at: datetime
    updated_at: datetime


class ChatCompletionRequestLogsList(BaseSchema):
    requests: list[ChatCompletionRequestLog]
    total: int
    limit: int
    offset: int


class ChatCompletionStatusCount(BaseSchema):
    status: ChatCompletionRequestStatus
    count: int


class ChatCompletionModelStats(BaseSchema):
    model_public_id: str
    requests: int
    total_tokens: int | None
    avg_total_ms: float | None


class ChatCompletionStats(BaseSchema):
    total_requests: int
    by_status: list[ChatCompletionStatusCount]
    prompt_tokens_total: int | None
    completion_tokens_total: int | None
    total_tokens_total: int | None
    avg_embedding_ms: float | None
    avg_llm_ttfb_ms: float | None
    avg_llm_generation_ms: float | None
    avg_total_ms: float | None
    by_model: list[ChatCompletionModelStats]


OpenAIChunk = dict[str, Any]
