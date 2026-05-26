from datetime import datetime
from uuid import UUID

from pydantic import Field

from rag_service.schema import BaseSchema


class ApiKeyCreate(BaseSchema):
    name: str | None = Field(default=None, max_length=255)
    expires_at: datetime | None = None


class ApiKey(BaseSchema):
    id: UUID
    name: str | None
    key_prefix: str
    user_id: UUID
    revoked_at: datetime | None
    expires_at: datetime | None
    last_used_at: datetime | None
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ApiKeyCreated(BaseSchema):
    api_key: str
    api_key_info: ApiKey
