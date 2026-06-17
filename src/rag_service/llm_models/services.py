from uuid import UUID

from advanced_alchemy.filters import LimitOffset, OrderBy
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from rag_service.exceptions import ConflictError, NotFoundError
from rag_service.llm_models.models import LlmModel
from rag_service.llm_models.repositories import LlmModelRepository


class LlmModelService(SQLAlchemyAsyncRepositoryService[LlmModel, LlmModelRepository]):
    """LLM Model Service"""

    repository_type = LlmModelRepository

    async def list_not_deleted(self) -> list[LlmModel]:
        """
        Return all LLM models that have not been soft-deleted.
        """
        models = await self.repository.list(LlmModel.deleted_at.is_(None))
        return list(models)

    async def list_paginated(self, limit: int, offset: int) -> tuple[list[LlmModel], int]:
        """
        Return a page of LLM models that have not been soft-deleted, with the total count.
        """
        models, total = await self.repository.list_and_count(
            LlmModel.deleted_at.is_(None),
            LimitOffset(limit=limit, offset=offset),
            OrderBy(field_name="created_at", sort_order="desc"),
        )
        return list(models), total

    async def create_model(
        self,
        public_id: str,
        provider_model: str,
        context_window_tokens: int,
        max_completion_tokens: int,
        provider: str = "ollama",
        description: str | None = None,
    ) -> LlmModel:
        """
        Create an LLM model.
        """
        await self.ensure_public_id_is_available(public_id)
        return await self.repository.add(
            LlmModel(
                public_id=public_id,
                provider=provider,
                provider_model=provider_model,
                context_window_tokens=context_window_tokens,
                max_completion_tokens=max_completion_tokens,
                description=description,
            ),
            auto_commit=True,
        )

    async def update_model(
        self,
        model_id: UUID,
        public_id: str | None = None,
        provider: str | None = None,
        provider_model: str | None = None,
        context_window_tokens: int | None = None,
        max_completion_tokens: int | None = None,
        description: str | None = None,
    ) -> LlmModel:
        """
        Update an active LLM model.
        """
        model = await self.get_by_id_or_raise(model_id)

        if public_id is not None and public_id != model.public_id:
            await self.ensure_public_id_is_available(public_id)
            model.public_id = public_id

        if provider is not None:
            model.provider = provider

        if provider_model is not None:
            model.provider_model = provider_model

        if context_window_tokens is not None:
            model.context_window_tokens = context_window_tokens

        if max_completion_tokens is not None:
            model.max_completion_tokens = max_completion_tokens

        if description is not None:
            model.description = description

        return await self.repository.update(model, auto_commit=True)

    async def delete_model(self, model_id: UUID) -> None:
        """
        Soft-delete an LLM model.
        """
        model = await self.get_by_id_or_raise(model_id)
        model.soft_delete()
        await self.repository.update(model, auto_commit=True)

    async def get_by_public_id_or_raise(self, public_id: str) -> LlmModel:
        """
        Return an active LLM model by public id.
        """
        model = await self.repository.get_one_or_none(
            LlmModel.deleted_at.is_(None),
            public_id=public_id,
        )

        if model is None:
            raise NotFoundError("Model not found")

        return model

    async def get_by_id_or_raise(self, model_id: UUID) -> LlmModel:
        """
        Return an LLM model by id.
        """
        model = await self.repository.get_one_or_none(
            LlmModel.deleted_at.is_(None),
            id=model_id,
        )

        if model is None:
            raise NotFoundError()

        return model

    async def ensure_public_id_is_available(self, public_id: str) -> None:
        """
        Ensure the public model id is not used.
        """
        existing_model = await self.repository.get_one_or_none(public_id=public_id)
        if existing_model is not None:
            raise ConflictError("Model public id already exists")
