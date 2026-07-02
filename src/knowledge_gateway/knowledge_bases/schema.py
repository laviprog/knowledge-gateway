from datetime import datetime
from uuid import UUID

from pydantic import Field

from knowledge_gateway.schema import BaseSchema, PaginatedList


class KnowledgeBaseCreate(BaseSchema):
    public_id: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    embedding_model_id: UUID
    description: str | None = None


class KnowledgeBaseUpdate(BaseSchema):
    public_id: str | None = Field(default=None, min_length=1, max_length=255)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class KnowledgeBase(BaseSchema):
    id: UUID
    public_id: str
    name: str
    embedding_model_id: UUID
    description: str | None
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class KnowledgeBasesList(PaginatedList):
    knowledge_bases: list[KnowledgeBase]
