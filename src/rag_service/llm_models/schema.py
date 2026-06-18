from datetime import datetime
from uuid import UUID

from pydantic import Field

from rag_service.schema import BaseSchema, PaginatedList


class LlmModelCreate(BaseSchema):
    public_id: str = Field(min_length=1, max_length=255)
    provider: str = Field(default="openai", min_length=1, max_length=50)
    provider_model: str = Field(min_length=1, max_length=255)
    context_window_tokens: int = Field(gt=0)
    max_completion_tokens: int = Field(gt=0)
    description: str | None = None


class LlmModelUpdate(BaseSchema):
    public_id: str | None = Field(default=None, min_length=1, max_length=255)
    provider: str | None = Field(default=None, min_length=1, max_length=50)
    provider_model: str | None = Field(default=None, min_length=1, max_length=255)
    context_window_tokens: int | None = Field(default=None, gt=0)
    max_completion_tokens: int | None = Field(default=None, gt=0)
    description: str | None = None


class LlmModel(BaseSchema):
    id: UUID
    public_id: str
    provider: str
    provider_model: str
    context_window_tokens: int
    max_completion_tokens: int
    description: str | None
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class LlmModelsList(PaginatedList):
    models: list[LlmModel]


class OpenAIModel(BaseSchema):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "syn"


class OpenAIModelsList(BaseSchema):
    object: str = "list"
    data: list[OpenAIModel]
