import asyncio
from uuid import UUID, uuid4

import pytest

from rag_service.exceptions import ConflictError, NotFoundError
from rag_service.llm_models.models import LlmModel
from rag_service.llm_models.services import LlmModelService


class FakeLlmModelRepository:
    def __init__(self, model: LlmModel | None = None) -> None:
        self.model = model
        self.added_model: LlmModel | None = None
        self.updated_model: LlmModel | None = None

    async def add(
        self,
        model: LlmModel,
        auto_commit: bool,
    ) -> LlmModel:
        self.added_model = model
        self.model = model
        return model

    async def update(
        self,
        model: LlmModel,
        auto_commit: bool,
    ) -> LlmModel:
        self.updated_model = model
        self.model = model
        return model

    async def list(self, *filters) -> list[LlmModel]:
        if self.model is None:
            return []

        return [self.model]

    async def get_one_or_none(self, *filters, **kwargs) -> LlmModel | None:
        if self.model is None:
            return None

        if public_id := kwargs.get("public_id"):
            if self.model.public_id == public_id:
                return self.model
            return None

        if model_id := kwargs.get("id"):
            if self.model.id == model_id:
                return self.model
            return None

        return self.model


class FakeLlmModelRepositoryWithDuplicate:
    def __init__(self, model: LlmModel, duplicate_model: LlmModel) -> None:
        self.model = model
        self.duplicate_model = duplicate_model

    async def get_one_or_none(self, *filters, **kwargs) -> LlmModel | None:
        if public_id := kwargs.get("public_id"):
            if self.duplicate_model.public_id == public_id:
                return self.duplicate_model
            return None

        if model_id := kwargs.get("id"):
            if self.model.id == model_id:
                return self.model
            return None

        return None


def create_model(model_id: UUID | None = None) -> LlmModel:
    return LlmModel(
        id=model_id or uuid4(),
        public_id="rag-assistant-lite",
        provider="openai",
        provider_model="llama3.1:8b",
        context_window_tokens=8192,
        max_completion_tokens=1024,
        description=None,
    )


def test_create_model_creates_llm_model() -> None:
    service = object.__new__(LlmModelService)
    service._repository_instance = FakeLlmModelRepository()

    model = asyncio.run(
        service.create_model(
            public_id="rag-assistant-lite",
            provider_model="llama3.1:8b",
            context_window_tokens=8192,
            max_completion_tokens=1024,
            provider_id=uuid4(),
        )
    )

    assert model.public_id == "rag-assistant-lite"
    assert model.provider == "openai"
    assert model.provider_model == "llama3.1:8b"


def test_create_model_rejects_duplicate_public_id() -> None:
    service = object.__new__(LlmModelService)
    service._repository_instance = FakeLlmModelRepository(create_model())

    with pytest.raises(ConflictError):
        asyncio.run(
            service.create_model(
                public_id="rag-assistant-lite",
                provider_model="llama3.1:8b",
                context_window_tokens=8192,
                max_completion_tokens=1024,
                provider_id=uuid4(),
            )
        )


def test_create_model_rejects_soft_deleted_duplicate_public_id() -> None:
    model = create_model()
    model.soft_delete()
    service = object.__new__(LlmModelService)
    service._repository_instance = FakeLlmModelRepository(model)

    with pytest.raises(ConflictError):
        asyncio.run(
            service.create_model(
                public_id="rag-assistant-lite",
                provider_model="llama3.1:8b",
                context_window_tokens=8192,
                max_completion_tokens=1024,
                provider_id=uuid4(),
            )
        )


def test_get_by_public_id_raises_not_found() -> None:
    service = object.__new__(LlmModelService)
    service._repository_instance = FakeLlmModelRepository()

    with pytest.raises(NotFoundError):
        asyncio.run(service.get_by_public_id_or_raise("missing-model"))


def test_update_model_rejects_duplicate_public_id() -> None:
    model = create_model()
    duplicate_model = create_model()
    duplicate_model.public_id = "rag-assistant-pro"
    service = object.__new__(LlmModelService)
    service._repository_instance = FakeLlmModelRepositoryWithDuplicate(
        model=model,
        duplicate_model=duplicate_model,
    )

    with pytest.raises(ConflictError):
        asyncio.run(
            service.update_model(
                model_id=model.id,
                public_id="rag-assistant-pro",
            )
        )


def test_delete_model_soft_deletes_model() -> None:
    model = create_model()
    service = object.__new__(LlmModelService)
    service._repository_instance = FakeLlmModelRepository(model)

    asyncio.run(service.delete_model(model.id))

    assert model.is_deleted
    assert service.repository.updated_model == model
