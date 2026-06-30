from uuid import UUID

from advanced_alchemy.filters import LimitOffset, OrderBy
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from rag_service.embedding_models.models import EmbeddingModel
from rag_service.embedding_models.repositories import EmbeddingModelRepository
from rag_service.exceptions import ConflictError, NotFoundError
from rag_service.knowledge_bases.models import KnowledgeBaseModel
from rag_service.knowledge_bases.repositories import KnowledgeBaseRepository


class KnowledgeBaseService(
    SQLAlchemyAsyncRepositoryService[KnowledgeBaseModel, KnowledgeBaseRepository]
):
    """Knowledge Base Service"""

    repository_type = KnowledgeBaseRepository

    def __init__(self, session, **kwargs):
        super().__init__(session=session, **kwargs)
        self.embedding_model_repository = EmbeddingModelRepository(session=session)

    async def list_paginated(self, limit: int, offset: int) -> tuple[list[KnowledgeBaseModel], int]:
        """
        Return a page of knowledge bases that have not been soft-deleted, with the total count.
        """
        knowledge_bases, total = await self.repository.list_and_count(
            KnowledgeBaseModel.deleted_at.is_(None),
            LimitOffset(limit=limit, offset=offset),
            OrderBy(field_name="created_at", sort_order="desc"),
        )
        return list(knowledge_bases), total

    async def create_knowledge_base(
        self,
        public_id: str,
        name: str,
        embedding_model_id: UUID,
        description: str | None = None,
    ) -> KnowledgeBaseModel:
        """
        Create a knowledge base bound to an existing embedding model.
        """
        await self.ensure_public_id_is_available(public_id)
        await self.ensure_embedding_model_exists(embedding_model_id)

        return await self.repository.add(
            KnowledgeBaseModel(
                public_id=public_id,
                name=name,
                embedding_model_id=embedding_model_id,
                description=description,
            ),
            auto_commit=True,
        )

    async def update_knowledge_base(
        self,
        knowledge_base_id: UUID,
        public_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
    ) -> KnowledgeBaseModel:
        """
        Update an active knowledge base.

        The embedding model is immutable: changing it would require re-indexing every document,
        so a new knowledge base must be created instead.
        """
        knowledge_base = await self.get_by_id_or_raise(knowledge_base_id)

        if public_id is not None and public_id != knowledge_base.public_id:
            await self.ensure_public_id_is_available(public_id)
            knowledge_base.public_id = public_id

        if name is not None:
            knowledge_base.name = name

        if description is not None:
            knowledge_base.description = description

        return await self.repository.update(knowledge_base, auto_commit=True)

    async def delete_knowledge_base(self, knowledge_base_id: UUID) -> None:
        """
        Soft-delete a knowledge base.
        """
        knowledge_base = await self.get_by_id_or_raise(knowledge_base_id)
        knowledge_base.soft_delete()
        await self.repository.update(knowledge_base, auto_commit=True)

    async def get_by_id_or_raise(self, knowledge_base_id: UUID) -> KnowledgeBaseModel:
        """
        Return an active knowledge base by id.
        """
        knowledge_base = await self.get_by_id_or_none(knowledge_base_id)

        if knowledge_base is None:
            raise NotFoundError("Knowledge base not found")

        return knowledge_base

    async def get_by_id_or_none(self, knowledge_base_id: UUID) -> KnowledgeBaseModel | None:
        """
        Return an active knowledge base by id, or ``None`` when it does not exist.
        """
        return await self.repository.get_one_or_none(
            KnowledgeBaseModel.deleted_at.is_(None),
            id=knowledge_base_id,
        )

    async def get_by_public_id_or_raise(self, public_id: str) -> KnowledgeBaseModel:
        """
        Return an active knowledge base by public id.
        """
        knowledge_base = await self.get_by_public_id_or_none(public_id)

        if knowledge_base is None:
            raise NotFoundError("Knowledge base not found")

        return knowledge_base

    async def get_by_public_id_or_none(self, public_id: str) -> KnowledgeBaseModel | None:
        """
        Return an active knowledge base by public id, or ``None`` when it does not exist.
        """
        return await self.repository.get_one_or_none(
            KnowledgeBaseModel.deleted_at.is_(None),
            public_id=public_id,
        )

    async def ensure_public_id_is_available(self, public_id: str) -> None:
        """
        Ensure the knowledge base public id is not used.
        """
        existing = await self.repository.get_one_or_none(public_id=public_id)
        if existing is not None:
            raise ConflictError("Knowledge base public id already exists")

    async def ensure_embedding_model_exists(self, embedding_model_id: UUID) -> None:
        """
        Ensure the referenced embedding model exists and is active.
        """
        embedding_model = await self.embedding_model_repository.get_one_or_none(
            EmbeddingModel.deleted_at.is_(None),
            id=embedding_model_id,
        )
        if embedding_model is None:
            raise NotFoundError("Embedding model not found")
