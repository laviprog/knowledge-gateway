from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rag_service.database.base_model import BaseModel
from rag_service.security.encryption import EncryptedString

if TYPE_CHECKING:
    from rag_service.llm_models.models import LlmModel


class ProviderModel(BaseModel):
    """
    OpenAI-compatible inference provider (base URL + credentials), referenced by LLM models.
    """

    __tablename__ = "providers"

    public_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    base_url: Mapped[str] = mapped_column(String(512))
    # Stored encrypted at rest; nullable for providers that need no key (e.g. local vLLM/Ollama).
    api_key: Mapped[str | None] = mapped_column(EncryptedString(1024))
    timeout_seconds: Mapped[float | None]
    max_retries: Mapped[int | None]
    description: Mapped[str | None]

    llm_models: Mapped[list["LlmModel"]] = relationship(
        "LlmModel",
        back_populates="inference_provider",
        lazy="selectin",
    )
