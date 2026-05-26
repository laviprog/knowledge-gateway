from datetime import datetime
from uuid import UUID

from pydantic import Field

from rag_service.schema import BaseSchema
from rag_service.users.models import Role


class UserCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=255)
    role: Role = Role.USER


class User(BaseSchema):
    id: UUID
    name: str
    role: Role
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class UsersList(BaseSchema):
    users: list[User]
