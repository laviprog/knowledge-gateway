from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from knowledge_gateway.database.base_model import BaseModel

if TYPE_CHECKING:
    from knowledge_gateway.embedding_models.models import EmbeddingModel


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

    # Optional per-knowledge-base retrieval overrides; fall back to the global settings when unset.
    # Minimum similarity score a retrieved chunk must reach to be used as context.
    min_score: Mapped[float | None] = mapped_column(Float)
    # System instruction prepended to the RAG prompt for this knowledge base.
    system_prompt: Mapped[str | None] = mapped_column(Text)

    embedding_model_id: Mapped[UUID] = mapped_column(ForeignKey("embedding_models.id"), index=True)
    embedding_model: Mapped["EmbeddingModel"] = relationship(
        "EmbeddingModel",
        lazy="selectin",
    )

    @property
    def embedding_model_public_id(self) -> str | None:
        return self.embedding_model.public_id if self.embedding_model is not None else None
