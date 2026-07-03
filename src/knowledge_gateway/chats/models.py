from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from knowledge_gateway.database.base_model import BaseModel
from knowledge_gateway.enums import BaseEnum

if TYPE_CHECKING:
    from knowledge_gateway.api_keys.models import ApiKeyModel
    from knowledge_gateway.knowledge_bases.models import KnowledgeBaseModel
    from knowledge_gateway.llm_models.models import LlmModel
    from knowledge_gateway.users.models import UserModel


class ChatCompletionRequestStatus(BaseEnum):
    """
    Chat completion request lifecycle status.
    """

    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


class ChatCompletionRequestLogModel(BaseModel):
    """
    Persisted chat completion request usage and latency metrics.
    """

    __tablename__ = "chat_completion_requests"

    api_key_id: Mapped[UUID] = mapped_column(ForeignKey("api_keys.id"), index=True)
    api_key: Mapped["ApiKeyModel"] = relationship(
        "ApiKeyModel",
        back_populates="chat_completion_requests",
        lazy="selectin",
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="chat_completion_requests",
        lazy="selectin",
    )

    model_id: Mapped[UUID | None] = mapped_column(ForeignKey("llm_models.id"), index=True)
    llm_model: Mapped["LlmModel | None"] = relationship(
        "LlmModel",
        back_populates="chat_completion_requests",
        lazy="selectin",
    )

    model_public_id: Mapped[str] = mapped_column(String(255), index=True)
    provider: Mapped[str | None] = mapped_column(String(50))
    provider_model: Mapped[str | None] = mapped_column(String(255))

    # Retrieval context: which knowledge base (if any) served this request and whether RAG ran.
    knowledge_base_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("knowledge_bases.id"), index=True
    )
    knowledge_base: Mapped["KnowledgeBaseModel | None"] = relationship(
        "KnowledgeBaseModel",
        lazy="selectin",
    )
    knowledge_base_public_id: Mapped[str | None] = mapped_column(String(255), index=True)
    used_retrieval: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    # Distinct document ids whose chunks were retrieved for this request (for search-quality
    # analysis). No message or chunk content is persisted.
    retrieved_document_ids: Mapped[list[str] | None] = mapped_column(JSONB)

    request_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    completion_id: Mapped[str | None] = mapped_column(String(255), index=True)
    stream: Mapped[bool] = mapped_column(Boolean)
    status: Mapped[ChatCompletionRequestStatus] = mapped_column(
        Enum(ChatCompletionRequestStatus),
        index=True,
    )
    error_code: Mapped[str | None] = mapped_column(String(255))
    error_message: Mapped[str | None] = mapped_column(Text)

    prompt_tokens: Mapped[int | None]
    completion_tokens: Mapped[int | None]
    total_tokens: Mapped[int | None]

    chunks_count: Mapped[int | None]
    retrieval_total_ms: Mapped[float | None] = mapped_column(Float)
    embedding_ms: Mapped[float | None] = mapped_column(Float)
    qdrant_search_ms: Mapped[float | None] = mapped_column(Float)
    llm_ttfb_ms: Mapped[float | None] = mapped_column(Float)
    llm_generation_ms: Mapped[float | None] = mapped_column(Float)
    total_ms: Mapped[float | None] = mapped_column(Float)

    messages_count: Mapped[int | None]
    query_length: Mapped[int | None]
