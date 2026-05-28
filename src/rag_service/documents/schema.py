from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from rag_service.schema import BaseSchema


class DocumentCreate(BaseSchema):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    source: str | None = Field(default=None, max_length=512)
    source_metadata: dict[str, Any] = Field(default_factory=dict)


class Document(BaseSchema):
    id: UUID
    title: str
    content: str
    content_hash: str
    source: str | None
    source_metadata: dict[str, Any]
    chunks_count: int
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class DocumentsList(BaseSchema):
    documents: list[Document]
