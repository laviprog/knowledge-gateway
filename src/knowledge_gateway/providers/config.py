from knowledge_gateway.llm.client import ProviderConfig
from knowledge_gateway.providers.models import ProviderModel

# Applied when a provider record leaves these tuning fields unset.
DEFAULT_PROVIDER_TIMEOUT_SECONDS = 30.0
DEFAULT_PROVIDER_MAX_RETRIES = 2


def resolve_provider_config(provider: ProviderModel) -> ProviderConfig:
    """
    Resolve provider connection config from a provider record, applying per-field defaults
    (timeout / retries) when the record leaves them unset.
    """
    return ProviderConfig(
        base_url=provider.base_url,
        api_key=provider.api_key,
        timeout_seconds=(
            provider.timeout_seconds
            if provider.timeout_seconds is not None
            else DEFAULT_PROVIDER_TIMEOUT_SECONDS
        ),
        max_retries=(
            provider.max_retries
            if provider.max_retries is not None
            else DEFAULT_PROVIDER_MAX_RETRIES
        ),
    )
