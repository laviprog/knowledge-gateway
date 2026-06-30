import asyncio
from uuid import UUID, uuid4

import pytest

from rag_service.embedding_models.models import EmbeddingModel
from rag_service.embedding_models.services import EmbeddingModelService
from rag_service.exceptions import ConflictError, NotFoundError


class FakeEmbeddingModelRepository:
    def __init__(self, model: EmbeddingModel | None = None) -> None:
        self.model = model
        self.added_model: EmbeddingModel | None = None
        self.updated_model: EmbeddingModel | None = None

    async def add(self, model: EmbeddingModel, auto_commit: bool) -> EmbeddingModel:
        self.added_model = model
        self.model = model
        return model

    async def update(self, model: EmbeddingModel, auto_commit: bool) -> EmbeddingModel:
        self.updated_model = model
        self.model = model
        return model

    async def get_one_or_none(self, *filters, **kwargs) -> EmbeddingModel | None:
        if self.model is None:
            return None

        if public_id := kwargs.get("public_id"):
            return self.model if self.model.public_id == public_id else None

        if collection_name := kwargs.get("collection_name"):
            return self.model if self.model.collection_name == collection_name else None

        if model_id := kwargs.get("id"):
            return self.model if self.model.id == model_id else None

        return self.model


def build_embedding_model(model_id: UUID | None = None) -> EmbeddingModel:
    return EmbeddingModel(
        id=model_id or uuid4(),
        public_id="default",
        provider_model="bge-m3",
        dimension=1024,
        collection_name="kb_emb_default",
        provider_id=uuid4(),
    )


def test_create_embedding_model_defaults_collection_name() -> None:
    service = object.__new__(EmbeddingModelService)
    service._repository_instance = FakeEmbeddingModelRepository()

    model = asyncio.run(
        service.create_embedding_model(
            public_id="bge",
            provider_model="bge-m3",
            provider_id=uuid4(),
        )
    )

    assert model.public_id == "bge"
    assert model.collection_name == "kb_emb_bge"


def test_create_embedding_model_rejects_duplicate_public_id() -> None:
    service = object.__new__(EmbeddingModelService)
    service._repository_instance = FakeEmbeddingModelRepository(build_embedding_model())

    with pytest.raises(ConflictError):
        asyncio.run(
            service.create_embedding_model(
                public_id="default",
                provider_model="bge-m3",
                provider_id=uuid4(),
            )
        )


def test_create_embedding_model_rejects_duplicate_collection_name() -> None:
    service = object.__new__(EmbeddingModelService)
    service._repository_instance = FakeEmbeddingModelRepository(build_embedding_model())

    with pytest.raises(ConflictError):
        asyncio.run(
            service.create_embedding_model(
                public_id="other",
                provider_model="bge-m3",
                provider_id=uuid4(),
                collection_name="kb_emb_default",
            )
        )


def test_get_by_id_raises_not_found() -> None:
    service = object.__new__(EmbeddingModelService)
    service._repository_instance = FakeEmbeddingModelRepository()

    with pytest.raises(NotFoundError):
        asyncio.run(service.get_by_id_or_raise(uuid4()))


def test_delete_embedding_model_soft_deletes() -> None:
    model = build_embedding_model()
    service = object.__new__(EmbeddingModelService)
    service._repository_instance = FakeEmbeddingModelRepository(model)

    asyncio.run(service.delete_embedding_model(model.id))

    assert model.is_deleted
    assert service.repository.updated_model == model
