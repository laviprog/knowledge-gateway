from typing import Any, ClassVar, Literal

from pydantic import ConfigDict, Field

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
    think: bool | Literal["low", "medium", "high"] | None = False

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


OpenAIChunk = dict[str, Any]
