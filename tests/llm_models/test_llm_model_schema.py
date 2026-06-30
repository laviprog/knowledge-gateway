from datetime import UTC, datetime
from uuid import uuid4

from rag_service.llm_models.models import LlmModel
from rag_service.llm_models.schema import LlmModel as LlmModelSchema
from rag_service.llm_models.schema import OpenAIModel, OpenAIModelsList


def test_llm_model_schema_validates_model() -> None:
    created_at = datetime(2026, 5, 29, tzinfo=UTC)
    model = LlmModel(
        id=uuid4(),
        public_id="rag-assistant-lite",
        provider="openai",
        provider_model="llama3.1:8b",
        context_window_tokens=8192,
        max_completion_tokens=1024,
        provider_id=uuid4(),
        description="Fast assistant model",
        created_at=created_at,
        updated_at=created_at,
    )

    schema = LlmModelSchema.model_validate(model)

    assert schema.public_id == "rag-assistant-lite"
    assert schema.provider == "openai"
    assert schema.provider_model == "llama3.1:8b"


def test_openai_models_list_uses_openai_compatible_shape() -> None:
    created_at = datetime(2026, 5, 29, tzinfo=UTC)

    models_list = OpenAIModelsList(
        data=[
            OpenAIModel(
                id="rag-assistant-lite",
                created=int(created_at.timestamp()),
            )
        ],
    )

    assert models_list.model_dump() == {
        "object": "list",
        "data": [
            {
                "id": "rag-assistant-lite",
                "object": "model",
                "created": 1780012800,
                "owned_by": "syn",
            }
        ],
    }
