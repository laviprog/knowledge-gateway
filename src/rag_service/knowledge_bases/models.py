from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rag_service.database.base_model import BaseModel

if TYPE_CHECKING:
    from rag_service.embedding_models.models import EmbeddingModel


class KnowledgeBaseModel(BaseModel):
    """
    A knowledge base: a named corpus of documents indexed with a single embedding model.

    The embedding model determines the vector space (and Qdrant collection); it is fixed at
    creation, since changing it would require re-indexing every document.
    """

    __tablename__ = "knowledge_bases"

    public_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None]

    embedding_model_id: Mapped[UUID] = mapped_column(ForeignKey("embedding_models.id"), index=True)
    embedding_model: Mapped["EmbeddingModel"] = relationship(
        "EmbeddingModel",
        lazy="selectin",
    )
