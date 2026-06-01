from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rag_service.database.base_model import BaseModel

if TYPE_CHECKING:
    from rag_service.chats.models import ChatCompletionRequestLogModel
    from rag_service.users.models import UserModel


class ApiKeyModel(BaseModel):
    """
    API Key model representing API keys for accessing the application.
    """

    __tablename__ = "api_keys"

    name: Mapped[str | None] = mapped_column(String(255))

    key_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    key_prefix: Mapped[str] = mapped_column(String(15))

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="api_keys", lazy="selectin"
    )
    chat_completion_requests: Mapped[list["ChatCompletionRequestLogModel"]] = relationship(
        "ChatCompletionRequestLogModel",
        back_populates="api_key",
        lazy="selectin",
    )

    expires_at: Mapped[datetime | None]
    revoked_at: Mapped[datetime | None]
    last_used_at: Mapped[datetime | None]
