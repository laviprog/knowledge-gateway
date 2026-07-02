from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import Field

from knowledge_gateway.schema import BaseSchema, PaginatedList

if TYPE_CHECKING:
    from knowledge_gateway.providers.models import ProviderModel


class ProviderCreate(BaseSchema):
    public_id: str = Field(min_length=1, max_length=255)
    base_url: str = Field(min_length=1, max_length=512)
    api_key: str | None = Field(default=None, max_length=1024)
    timeout_seconds: float | None = Field(default=None, gt=0)
    max_retries: int | None = Field(default=None, ge=0)
    description: str | None = None


class ProviderUpdate(BaseSchema):
    public_id: str | None = Field(default=None, min_length=1, max_length=255)
    base_url: str | None = Field(default=None, min_length=1, max_length=512)
    api_key: str | None = Field(default=None, max_length=1024)
    timeout_seconds: float | None = Field(default=None, gt=0)
    max_retries: int | None = Field(default=None, ge=0)
    description: str | None = None


class Provider(BaseSchema):
    id: UUID
    public_id: str
    base_url: str
    # The stored secret is never returned; only whether one is set.
    has_api_key: bool
    timeout_seconds: float | None
    max_retries: int | None
    description: str | None
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, provider: "ProviderModel") -> "Provider":
        return cls(
            id=provider.id,
            public_id=provider.public_id,
            base_url=provider.base_url,
            has_api_key=provider.api_key is not None,
            timeout_seconds=provider.timeout_seconds,
            max_retries=provider.max_retries,
            description=provider.description,
            deleted_at=provider.deleted_at,
            created_at=provider.created_at,
            updated_at=provider.updated_at,
        )


class ProvidersList(PaginatedList):
    providers: list[Provider]
