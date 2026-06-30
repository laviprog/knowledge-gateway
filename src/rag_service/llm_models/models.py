from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rag_service.database.base_model import BaseModel

if TYPE_CHECKING:
    from rag_service.chats.models import ChatCompletionRequestLogModel
    from rag_service.providers.models import ProviderModel


class LlmModel(BaseModel):
    """
    LLM model available for chat completions.
    """

    __tablename__ = "llm_models"

    public_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    provider: Mapped[str] = mapped_column(String(50), default="openai")
    provider_model: Mapped[str] = mapped_column(String(255))
    context_window_tokens: Mapped[int]
    max_completion_tokens: Mapped[int]
    description: Mapped[str | None]

    # Concrete inference endpoint + credentials, required: providers live in the database.
    provider_id: Mapped[UUID] = mapped_column(ForeignKey("providers.id"), index=True)
    inference_provider: Mapped["ProviderModel"] = relationship(
        "ProviderModel",
        back_populates="llm_models",
        lazy="selectin",
    )

    chat_completion_requests: Mapped[list["ChatCompletionRequestLogModel"]] = relationship(
        "ChatCompletionRequestLogModel",
        back_populates="llm_model",
        lazy="selectin",
    )
