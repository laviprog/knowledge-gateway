from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import Field

from knowledge_gateway.documents.models import DocumentIndexStatus
from knowledge_gateway.schema import BaseSchema, PaginatedList

if TYPE_CHECKING:
    from knowledge_gateway.knowledge_bases.models import KnowledgeBaseModel
    from knowledge_gateway.knowledge_bases.services import KnowledgeBaseDocumentStats


class KnowledgeBaseCreate(BaseSchema):
    public_id: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    embedding_model_id: UUID
    description: str | None = None


class KnowledgeBaseUpdate(BaseSchema):
    public_id: str | None = Field(default=None, min_length=1, max_length=255)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class KnowledgeBaseIndexStatusCounts(BaseSchema):
    pending: int = 0
    indexing: int = 0
    indexed: int = 0
    failed: int = 0


class KnowledgeBase(BaseSchema):
    id: UUID
    public_id: str
    name: str
    embedding_model_id: UUID
    embedding_model_public_id: str | None
    description: str | None
    document_count: int = 0
    index_status_counts: KnowledgeBaseIndexStatusCounts = Field(
        default_factory=KnowledgeBaseIndexStatusCounts
    )
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(
        cls,
        knowledge_base: "KnowledgeBaseModel",
        stats: "KnowledgeBaseDocumentStats | None" = None,
    ) -> "KnowledgeBase":
        """
        Build the response from an ORM model plus optional document/indexing statistics.
        """
        schema = cls.model_validate(knowledge_base)
        if stats is not None:
            schema.document_count = stats.document_count
            schema.index_status_counts = KnowledgeBaseIndexStatusCounts(
                pending=stats.status_counts.get(DocumentIndexStatus.PENDING, 0),
                indexing=stats.status_counts.get(DocumentIndexStatus.INDEXING, 0),
                indexed=stats.status_counts.get(DocumentIndexStatus.INDEXED, 0),
                failed=stats.status_counts.get(DocumentIndexStatus.FAILED, 0),
            )
        return schema


class KnowledgeBasesList(PaginatedList):
    knowledge_bases: list[KnowledgeBase]
