from uuid import UUID

from pydantic import Field

from knowledge_gateway.schema import BaseSchema
from knowledge_gateway.users.models import Role


class LoginRequest(BaseSchema):
    name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1)


class SessionUser(BaseSchema):
    """The authenticated admin behind the current session."""

    id: UUID
    name: str
    role: Role
