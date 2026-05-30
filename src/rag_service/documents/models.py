from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rag_service.database.base_model import BaseModel
from rag_service.enums import BaseEnum

if TYPE_CHECKING:
    from collections.abc import Sequence


class DocumentIndexStatus(BaseEnum):
    """
    Document indexing status.
    """

    PENDING = "pending"
    INDEXING = "indexing"
    INDEXED = "indexed"
    FAILED = "failed"


class DocumentModel(BaseModel):
    """
    Document stored in the global knowledge base.
    """

    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    source: Mapped[str | None] = mapped_column(String(512))
    source_metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    index_status: Mapped[DocumentIndexStatus] = mapped_column(
        Enum(DocumentIndexStatus),
        default=DocumentIndexStatus.PENDING,
    )
    index_error: Mapped[str | None] = mapped_column(Text)
    indexed_at: Mapped[datetime | None]

    chunks: Mapped[list["DocumentChunkModel"]] = relationship(
        "DocumentChunkModel",
        back_populates="document",
        lazy="selectin",
    )

    @property
    def chunks_count(self) -> int:
        return len([chunk for chunk in self.chunks if not chunk.is_deleted])


class DocumentChunkModel(BaseModel):
    """
    Document chunk prepared for vector storage.
    """

    __tablename__ = "document_chunks"
    __table_args__: "Sequence[UniqueConstraint]" = (
        UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_document_chunks_document_id_chunk_index",
        ),
    )

    document_id: Mapped[UUID] = mapped_column(ForeignKey("documents.id"), index=True)
    document: Mapped["DocumentModel"] = relationship(
        "DocumentModel",
        back_populates="chunks",
        lazy="selectin",
    )

    chunk_index: Mapped[int]
    content: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    token_count: Mapped[int | None]
    qdrant_point_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
