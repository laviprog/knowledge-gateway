import asyncio
from uuid import UUID, uuid4

import pytest

from knowledge_gateway.embedding_models.models import EmbeddingModel
from knowledge_gateway.exceptions import ConflictError, NotFoundError
from knowledge_gateway.knowledge_bases.models import KnowledgeBaseModel
from knowledge_gateway.knowledge_bases.services import KnowledgeBaseService


class FakeKnowledgeBaseRepository:
    def __init__(self, knowledge_base: KnowledgeBaseModel | None = None) -> None:
        self.knowledge_base = knowledge_base
        self.added: KnowledgeBaseModel | None = None
        self.updated: KnowledgeBaseModel | None = None

    async def add(
        self, knowledge_base: KnowledgeBaseModel, auto_commit: bool
    ) -> KnowledgeBaseModel:
        self.added = knowledge_base
        self.knowledge_base = knowledge_base
        return knowledge_base

    async def update(
        self, knowledge_base: KnowledgeBaseModel, auto_commit: bool
    ) -> KnowledgeBaseModel:
        self.updated = knowledge_base
        self.knowledge_base = knowledge_base
        return knowledge_base

    async def get_one_or_none(self, *filters, **kwargs) -> KnowledgeBaseModel | None:
        if self.knowledge_base is None:
            return None

        if public_id := kwargs.get("public_id"):
            return self.knowledge_base if self.knowledge_base.public_id == public_id else None

        if kb_id := kwargs.get("id"):
            return self.knowledge_base if self.knowledge_base.id == kb_id else None

        return self.knowledge_base


class FakeEmbeddingModelRepository:
    def __init__(self, embedding_model: EmbeddingModel | None = None) -> None:
        self.embedding_model = embedding_model

    async def get_one_or_none(self, *filters, **kwargs) -> EmbeddingModel | None:
        if self.embedding_model is None:
            return None

        if model_id := kwargs.get("id"):
            return self.embedding_model if self.embedding_model.id == model_id else None

        return self.embedding_model


def build_embedding_model(model_id: UUID | None = None) -> EmbeddingModel:
    return EmbeddingModel(
        id=model_id or uuid4(),
        public_id="default",
        provider_model="bge-m3",
        dimension=1024,
        collection_name="kb_emb_default",
        provider_id=uuid4(),
    )


def build_service(
    knowledge_base: KnowledgeBaseModel | None = None,
    embedding_model: EmbeddingModel | None = None,
) -> KnowledgeBaseService:
    service = object.__new__(KnowledgeBaseService)
    service._repository_instance = FakeKnowledgeBaseRepository(knowledge_base)
    service.embedding_model_repository = FakeEmbeddingModelRepository(embedding_model)
    return service


def test_create_knowledge_base_creates_with_existing_embedding_model() -> None:
    embedding_model = build_embedding_model()
    service = build_service(embedding_model=embedding_model)

    knowledge_base = asyncio.run(
        service.create_knowledge_base(
            public_id="support",
            name="Support",
            embedding_model_id=embedding_model.id,
        )
    )

    assert knowledge_base.public_id == "support"
    assert knowledge_base.embedding_model_id == embedding_model.id


def test_create_knowledge_base_rejects_unknown_embedding_model() -> None:
    service = build_service(embedding_model=None)

    with pytest.raises(NotFoundError):
        asyncio.run(
            service.create_knowledge_base(
                public_id="support",
                name="Support",
                embedding_model_id=uuid4(),
            )
        )


def test_create_knowledge_base_rejects_duplicate_public_id() -> None:
    embedding_model = build_embedding_model()
    existing = KnowledgeBaseModel(
        id=uuid4(),
        public_id="support",
        name="Support",
        embedding_model_id=embedding_model.id,
    )
    service = build_service(knowledge_base=existing, embedding_model=embedding_model)

    with pytest.raises(ConflictError):
        asyncio.run(
            service.create_knowledge_base(
                public_id="support",
                name="Support",
                embedding_model_id=embedding_model.id,
            )
        )


def test_create_knowledge_base_persists_retrieval_overrides() -> None:
    embedding_model = build_embedding_model()
    service = build_service(embedding_model=embedding_model)

    knowledge_base = asyncio.run(
        service.create_knowledge_base(
            public_id="support",
            name="Support",
            embedding_model_id=embedding_model.id,
            min_score=0.6,
            system_prompt="You are the billing expert.",
        )
    )

    assert knowledge_base.min_score == 0.6
    assert knowledge_base.system_prompt == "You are the billing expert."


def test_update_knowledge_base_updates_retrieval_overrides() -> None:
    embedding_model = build_embedding_model()
    existing = KnowledgeBaseModel(
        id=uuid4(),
        public_id="support",
        name="Support",
        embedding_model_id=embedding_model.id,
        min_score=0.2,
        system_prompt="Old prompt.",
    )
    service = build_service(knowledge_base=existing, embedding_model=embedding_model)

    updated = asyncio.run(
        service.update_knowledge_base(
            knowledge_base_id=existing.id,
            min_score=0.8,
            system_prompt="New prompt.",
        )
    )

    assert updated.min_score == 0.8
    assert updated.system_prompt == "New prompt."


def test_update_knowledge_base_leaves_overrides_untouched_when_omitted() -> None:
    embedding_model = build_embedding_model()
    existing = KnowledgeBaseModel(
        id=uuid4(),
        public_id="support",
        name="Support",
        embedding_model_id=embedding_model.id,
        min_score=0.2,
        system_prompt="Keep me.",
    )
    service = build_service(knowledge_base=existing, embedding_model=embedding_model)

    updated = asyncio.run(
        service.update_knowledge_base(knowledge_base_id=existing.id, name="Renamed")
    )

    assert updated.name == "Renamed"
    assert updated.min_score == 0.2
    assert updated.system_prompt == "Keep me."


def test_get_by_public_id_or_none_returns_none_when_missing() -> None:
    service = build_service()

    assert asyncio.run(service.get_by_public_id_or_none("default")) is None
