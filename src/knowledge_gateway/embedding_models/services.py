import re
from uuid import UUID

from advanced_alchemy.filters import LimitOffset, OrderBy
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from knowledge_gateway.embedding_models.models import EmbeddingModel
from knowledge_gateway.embedding_models.repositories import EmbeddingModelRepository
from knowledge_gateway.exceptions import BadRequestError, ConflictError, NotFoundError

# Qdrant rejects characters such as ":" and "/" in collection names.
_VALID_COLLECTION_NAME = re.compile(r"^[a-zA-Z0-9_-]+$")


def _default_collection_name(public_id: str) -> str:
    """
    Derive a Qdrant-safe default collection name from an embedding model public id.
    """
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", public_id).strip("_")
    return f"kb_emb_{slug or 'default'}"


class EmbeddingModelService(
    SQLAlchemyAsyncRepositoryService[EmbeddingModel, EmbeddingModelRepository]
):
    """Embedding Model Service"""

    repository_type = EmbeddingModelRepository

    async def list_paginated(self, limit: int, offset: int) -> tuple[list[EmbeddingModel], int]:
        """
        Return a page of embedding models that have not been soft-deleted, with the total count.
        """
        models, total = await self.repository.list_and_count(
            EmbeddingModel.deleted_at.is_(None),
            LimitOffset(limit=limit, offset=offset),
            OrderBy(field_name="created_at", sort_order="desc"),
        )
        return list(models), total

    async def create_embedding_model(
        self,
        public_id: str,
        provider_model: str,
        provider_id: UUID,
        dimension: int | None = None,
        collection_name: str | None = None,
        description: str | None = None,
    ) -> EmbeddingModel:
        """
        Create an embedding model. The Qdrant collection name defaults to a sanitized
        ``kb_emb_<public_id>`` and, when given explicitly, must be Qdrant-safe.
        """
        await self.ensure_public_id_is_available(public_id)

        if collection_name is None:
            resolved_collection = _default_collection_name(public_id)
        elif _VALID_COLLECTION_NAME.match(collection_name):
            resolved_collection = collection_name
        else:
            raise BadRequestError("collection_name may only contain letters, digits, '_' and '-'")

        await self.ensure_collection_name_is_available(resolved_collection)

        return await self.repository.add(
            EmbeddingModel(
                public_id=public_id,
                provider_model=provider_model,
                dimension=dimension,
                collection_name=resolved_collection,
                provider_id=provider_id,
                description=description,
            ),
            auto_commit=True,
        )

    async def update_embedding_model(
        self,
        model_id: UUID,
        public_id: str | None = None,
        provider_model: str | None = None,
        dimension: int | None = None,
        provider_id: UUID | None = None,
        description: str | None = None,
    ) -> EmbeddingModel:
        """
        Update an active embedding model.

        ``collection_name`` is intentionally immutable: changing it would orphan indexed
        vectors. Recreate the embedding model (and re-index) to target a new collection.
        """
        model = await self.get_by_id_or_raise(model_id)

        if public_id is not None and public_id != model.public_id:
            await self.ensure_public_id_is_available(public_id)
            model.public_id = public_id

        if provider_model is not None:
            model.provider_model = provider_model

        if dimension is not None:
            model.dimension = dimension

        if provider_id is not None:
            model.provider_id = provider_id

        if description is not None:
            model.description = description

        return await self.repository.update(model, auto_commit=True)

    async def delete_embedding_model(self, model_id: UUID) -> None:
        """
        Soft-delete an embedding model.
        """
        model = await self.get_by_id_or_raise(model_id)
        model.soft_delete()
        await self.repository.update(model, auto_commit=True)

    async def get_by_id_or_raise(self, model_id: UUID) -> EmbeddingModel:
        """
        Return an active embedding model by id.
        """
        model = await self.repository.get_one_or_none(
            EmbeddingModel.deleted_at.is_(None),
            id=model_id,
        )

        if model is None:
            raise NotFoundError("Embedding model not found")

        return model

    async def ensure_public_id_is_available(self, public_id: str) -> None:
        """
        Ensure the embedding model public id is not used.
        """
        existing = await self.repository.get_one_or_none(public_id=public_id)
        if existing is not None:
            raise ConflictError("Embedding model public id already exists")

    async def ensure_collection_name_is_available(self, collection_name: str) -> None:
        """
        Ensure the Qdrant collection name is not already taken by another embedding model.
        """
        existing = await self.repository.get_one_or_none(collection_name=collection_name)
        if existing is not None:
            raise ConflictError("Embedding model collection name already exists")
