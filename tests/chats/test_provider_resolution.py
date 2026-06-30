from uuid import uuid4

from rag_service.chats.services import provider_config_for_model
from rag_service.config import settings
from rag_service.llm_models.models import LlmModel
from rag_service.providers.models import ProviderModel


def build_model(provider: ProviderModel | None) -> LlmModel:
    model = LlmModel(
        id=uuid4(),
        public_id="rag-assistant",
        provider="openai",
        provider_model="gpt-4o-mini",
        context_window_tokens=8192,
        max_completion_tokens=1024,
    )
    model.inference_provider = provider
    return model


def test_falls_back_to_default_provider_when_unset() -> None:
    config = provider_config_for_model(build_model(None))

    assert config.base_url == settings.LLM_BASE_URL
    assert config.api_key == settings.LLM_API_KEY
    assert config.timeout_seconds == settings.LLM_TIMEOUT_SECONDS
    assert config.max_retries == settings.LLM_MAX_RETRIES


def test_uses_provider_record_when_present() -> None:
    provider = ProviderModel(
        id=uuid4(),
        public_id="azure-openai",
        base_url="https://azure.example/v1",
        api_key="sk-azure",
        timeout_seconds=12.5,
        max_retries=5,
    )

    config = provider_config_for_model(build_model(provider))

    assert config.base_url == "https://azure.example/v1"
    assert config.api_key == "sk-azure"
    assert config.timeout_seconds == 12.5
    assert config.max_retries == 5


def test_provider_record_falls_back_to_settings_for_unset_fields() -> None:
    provider = ProviderModel(
        id=uuid4(),
        public_id="vllm-local",
        base_url="http://localhost:8000/v1",
        api_key=None,
        timeout_seconds=None,
        max_retries=None,
    )

    config = provider_config_for_model(build_model(provider))

    assert config.base_url == "http://localhost:8000/v1"
    assert config.api_key is None
    assert config.timeout_seconds == settings.LLM_TIMEOUT_SECONDS
    assert config.max_retries == settings.LLM_MAX_RETRIES
