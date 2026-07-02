from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from knowledge_gateway.schema import BaseSchema, PaginatedList
from knowledge_gateway.utils import utc_now


class ApiKeyCreate(BaseSchema):
    name: str | None = Field(default=None, max_length=255)
    expires_at: datetime | None = None

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, expires_at: datetime | None) -> datetime | None:
        if expires_at is None:
            return expires_at

        if expires_at.tzinfo is None or expires_at.utcoffset() is None:
            raise ValueError("expires_at must include timezone")

        if expires_at <= utc_now():
            raise ValueError("expires_at must be in the future")

        return expires_at


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


class ApiKeysList(PaginatedList):
    api_keys: list[ApiKey]
