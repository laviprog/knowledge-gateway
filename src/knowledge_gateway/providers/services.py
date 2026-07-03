from uuid import UUID

from advanced_alchemy.filters import LimitOffset, OrderBy
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from knowledge_gateway.exceptions import ConflictError, NotFoundError
from knowledge_gateway.providers.models import ProviderModel
from knowledge_gateway.providers.repositories import ProviderRepository


class ProviderService(SQLAlchemyAsyncRepositoryService[ProviderModel, ProviderRepository]):
    """Provider Service"""

    repository_type = ProviderRepository

    async def list_paginated(self, limit: int, offset: int) -> tuple[list[ProviderModel], int]:
        """
        Return a page of providers that have not been soft-deleted, with the total count.
        """
        providers, total = await self.repository.list_and_count(
            ProviderModel.deleted_at.is_(None),
            LimitOffset(limit=limit, offset=offset),
            OrderBy(field_name="created_at", sort_order="desc"),
        )
        return list(providers), total

    async def create_provider(
        self,
        public_id: str,
        base_url: str,
        api_key: str | None = None,
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
        description: str | None = None,
    ) -> ProviderModel:
        """
        Create an inference provider.
        """
        await self.ensure_public_id_is_available(public_id)
        return await self.repository.add(
            ProviderModel(
                public_id=public_id,
                base_url=base_url,
                api_key=api_key,
                timeout_seconds=timeout_seconds,
                max_retries=max_retries,
                description=description,
            ),
            auto_commit=True,
        )

    async def update_provider(
        self,
        provider_id: UUID,
        public_id: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
        description: str | None = None,
    ) -> ProviderModel:
        """
        Update an active inference provider.
        """
        provider = await self.get_by_id_or_raise(provider_id)

        if public_id is not None and public_id != provider.public_id:
            await self.ensure_public_id_is_available(public_id)
            provider.public_id = public_id

        if base_url is not None:
            provider.base_url = base_url

        if api_key is not None:
            provider.api_key = api_key

        if timeout_seconds is not None:
            provider.timeout_seconds = timeout_seconds

        if max_retries is not None:
            provider.max_retries = max_retries

        if description is not None:
            provider.description = description

        return await self.repository.update(provider, auto_commit=True)

    async def delete_provider(self, provider_id: UUID) -> None:
        """
        Soft-delete an inference provider.
        """
        provider = await self.get_by_id_or_raise(provider_id)
        provider.soft_delete()
        await self.repository.update(provider, auto_commit=True)

    async def get_by_id_or_raise(self, provider_id: UUID) -> ProviderModel:
        """
        Return an active provider by id.
        """
        provider = await self.repository.get_one_or_none(
            ProviderModel.deleted_at.is_(None),
            id=provider_id,
        )

        if provider is None:
            raise NotFoundError("Provider not found")

        return provider

    async def ensure_public_id_is_available(self, public_id: str) -> None:
        """
        Ensure the provider public id is not used.
        """
        existing_provider = await self.repository.get_one_or_none(public_id=public_id)
        if existing_provider is not None:
            raise ConflictError("Provider public id already exists")
