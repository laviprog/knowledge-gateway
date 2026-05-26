from typing import TYPE_CHECKING

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rag_service.database.base_model import BaseModel
from rag_service.enums import BaseEnum

if TYPE_CHECKING:
    from rag_service.api_keys.models import ApiKeyModel


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

    api_keys: Mapped[list["ApiKeyModel"]] = relationship(
        "ApiKeyModel",
        back_populates="user",
        lazy="selectin",
    )
