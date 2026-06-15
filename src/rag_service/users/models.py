from typing import TYPE_CHECKING

from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rag_service.database.base_model import BaseModel
from rag_service.enums import BaseEnum

if TYPE_CHECKING:
    from rag_service.api_keys.models import ApiKeyModel
    from rag_service.chats.models import ChatCompletionRequestLogModel


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
