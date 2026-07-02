from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from knowledge_gateway.database.base_model import BaseModel

if TYPE_CHECKING:
    from knowledge_gateway.providers.models import ProviderModel


class EmbeddingModel(BaseModel):
    """
    Embedding model used to index and query a knowledge base.

    Each embedding model owns one Qdrant collection (one vector space); knowledge bases that
    share an embedding model share its collection and are isolated by a ``knowledge_base_id``
    payload filter.
    """

    __tablename__ = "embedding_models"

    public_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    provider_model: Mapped[str] = mapped_column(String(255))
    # Vector size; nullable when unknown (then inferred/validated lazily on first index).
    dimension: Mapped[int | None] = mapped_column(Integer)
    collection_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)

    # Concrete inference endpoint + credentials, required: providers live in the database.
    provider_id: Mapped[UUID] = mapped_column(ForeignKey("providers.id"), index=True)
    inference_provider: Mapped["ProviderModel"] = relationship(
        "ProviderModel",
        back_populates="embedding_models",
        lazy="selectin",
    )
