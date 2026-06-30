from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from rag_service.documents.models import DocumentIndexStatus
from rag_service.schema import BaseSchema, PaginatedList


class DocumentCreate(BaseSchema):
    knowledge_base_id: UUID
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    source: str | None = Field(default=None, max_length=512)
    source_metadata: dict[str, Any] = Field(default_factory=dict)


class Document(BaseSchema):
    id: UUID
    knowledge_base_id: UUID
    title: str
    content: str
    content_hash: str
    source: str | None
    source_metadata: dict[str, Any]
    chunks_count: int
    index_status: DocumentIndexStatus
    index_error: str | None
    indexed_at: datetime | None
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class DocumentsList(PaginatedList):
    documents: list[Document]


class DocumentSearchQuery(BaseSchema):
    knowledge_base_id: UUID
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)


class DocumentSearchResult(BaseSchema):
    score: float
    document_id: UUID
    chunk_id: UUID
    chunk_index: int
    content: str


class DocumentSearchResults(BaseSchema):
    results: list[DocumentSearchResult]
