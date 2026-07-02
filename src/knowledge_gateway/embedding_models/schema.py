from datetime import datetime
from uuid import UUID

from pydantic import Field

from knowledge_gateway.schema import BaseSchema, PaginatedList


class EmbeddingModelCreate(BaseSchema):
    public_id: str = Field(min_length=1, max_length=255)
    provider_model: str = Field(min_length=1, max_length=255)
    dimension: int | None = Field(default=None, gt=0)
    collection_name: str | None = Field(default=None, min_length=1, max_length=255)
    provider_id: UUID
    description: str | None = None


class EmbeddingModelUpdate(BaseSchema):
    public_id: str | None = Field(default=None, min_length=1, max_length=255)
    provider_model: str | None = Field(default=None, min_length=1, max_length=255)
    dimension: int | None = Field(default=None, gt=0)
    provider_id: UUID | None = None
    description: str | None = None


class EmbeddingModel(BaseSchema):
    id: UUID
    public_id: str
    provider_model: str
    dimension: int | None
    collection_name: str
    provider_id: UUID
    description: str | None
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class EmbeddingModelsList(PaginatedList):
    models: list[EmbeddingModel]
