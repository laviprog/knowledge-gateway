from typing import TYPE_CHECKING

from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from knowledge_gateway.database.base_model import BaseModel
from knowledge_gateway.enums import BaseEnum

if TYPE_CHECKING:
    from knowledge_gateway.api_keys.models import ApiKeyModel
    from knowledge_gateway.chats.models import ChatCompletionRequestLogModel


class Role(BaseEnum):
    """
    Enumeration for user roles.
    """

    ADMIN = "admin"
    USER = "user"


class UserModel(BaseModel):
    """
    User model representing users of the application.
    """

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.USER)
    requests_per_minute: Mapped[int] = mapped_column(Integer, default=60)

    # Argon2 hash for interactive (admin panel) login. Null for API-only users who never log in
    # via password.
    password_hash: Mapped[str | None] = mapped_column(String(255), default=None)

    api_keys: Mapped[list["ApiKeyModel"]] = relationship(
        "ApiKeyModel",
        back_populates="user",
        lazy="selectin",
    )
    chat_completion_requests: Mapped[list["ChatCompletionRequestLogModel"]] = relationship(
        "ChatCompletionRequestLogModel",
        back_populates="user",
        lazy="selectin",
    )
