from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from rag_service.database.base_model import BaseModel


class LlmModel(BaseModel):
    """
    LLM model available for chat completions.
    """

    __tablename__ = "llm_models"

    public_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    provider: Mapped[str] = mapped_column(String(50), default="ollama")
    provider_model: Mapped[str] = mapped_column(String(255))
    context_window_tokens: Mapped[int]
    max_completion_tokens: Mapped[int]
    description: Mapped[str | None] = mapped_column(Text)
