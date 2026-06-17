from datetime import datetime
from uuid import UUID

from pydantic import Field

from rag_service.config import settings
from rag_service.schema import BaseSchema, PaginatedList
from rag_service.users.models import Role


class UserCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=255)
    role: Role = Role.USER
    requests_per_minute: int = Field(default=settings.RATE_LIMIT_DEFAULT_REQUESTS_PER_MINUTE, ge=0)


class UserUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    role: Role | None = None
    requests_per_minute: int | None = Field(default=None, ge=0)


class User(BaseSchema):
    id: UUID
    name: str
    role: Role
    requests_per_minute: int
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class UsersList(PaginatedList):
    users: list[User]
