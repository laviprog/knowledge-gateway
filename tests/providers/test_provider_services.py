import asyncio
from uuid import UUID, uuid4

import pytest

from knowledge_gateway.exceptions import ConflictError, NotFoundError
from knowledge_gateway.providers.models import ProviderModel
from knowledge_gateway.providers.services import ProviderService


class FakeProviderRepository:
    def __init__(self, provider: ProviderModel | None = None) -> None:
        self.provider = provider
        self.added_provider: ProviderModel | None = None
        self.updated_provider: ProviderModel | None = None

    async def add(self, provider: ProviderModel, auto_commit: bool) -> ProviderModel:
        self.added_provider = provider
        self.provider = provider
        return provider

    async def update(self, provider: ProviderModel, auto_commit: bool) -> ProviderModel:
        self.updated_provider = provider
        self.provider = provider
        return provider

    async def get_one_or_none(self, *filters, **kwargs) -> ProviderModel | None:
        if self.provider is None:
            return None

        if public_id := kwargs.get("public_id"):
            return self.provider if self.provider.public_id == public_id else None

        if provider_id := kwargs.get("id"):
            return self.provider if self.provider.id == provider_id else None

        return self.provider


def build_provider(provider_id: UUID | None = None) -> ProviderModel:
    return ProviderModel(
        id=provider_id or uuid4(),
        public_id="openai-main",
        base_url="https://api.openai.com/v1",
        api_key="sk-secret",
        timeout_seconds=30,
        max_retries=2,
        description=None,
    )


def test_create_provider_creates_provider() -> None:
    service = object.__new__(ProviderService)
    service._repository_instance = FakeProviderRepository()

    provider = asyncio.run(
        service.create_provider(
            public_id="openai-main",
            base_url="https://api.openai.com/v1",
            api_key="sk-secret",
        )
    )

    assert provider.public_id == "openai-main"
    assert provider.base_url == "https://api.openai.com/v1"
    assert provider.api_key == "sk-secret"


def test_create_provider_rejects_duplicate_public_id() -> None:
    service = object.__new__(ProviderService)
    service._repository_instance = FakeProviderRepository(build_provider())

    with pytest.raises(ConflictError):
        asyncio.run(
            service.create_provider(
                public_id="openai-main",
                base_url="https://api.openai.com/v1",
            )
        )


def test_get_by_id_raises_not_found() -> None:
    service = object.__new__(ProviderService)
    service._repository_instance = FakeProviderRepository()

    with pytest.raises(NotFoundError):
        asyncio.run(service.get_by_id_or_raise(uuid4()))


def test_delete_provider_soft_deletes_provider() -> None:
    provider = build_provider()
    service = object.__new__(ProviderService)
    service._repository_instance = FakeProviderRepository(provider)

    asyncio.run(service.delete_provider(provider.id))

    assert provider.is_deleted
    assert service.repository.updated_provider == provider
