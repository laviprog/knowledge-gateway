import hashlib
import hmac
import secrets

from rag_service.config import settings

_PEPPER = settings.API_KEY_PEPPER.encode()


def generate_raw_api_key(
    prefix: str | None = None,
    token_length: int = 32,
    key_preview_length: int = 12,
) -> tuple[str, str]:
    """
    Generate a cryptographically secure API key.
    """
    prefix = prefix or settings.API_KEY_DEFAULT_PREFIX
    random_token = secrets.token_urlsafe(token_length)
    api_key = f"{prefix}_{random_token}"
    return api_key, api_key[:key_preview_length]


def hash_api_key(api_key: str) -> str:
    """
    Generate a secure HMAC-SHA256 hash for an API key.
    """
    return hmac.HMAC(
        _PEPPER,
        api_key.encode(),
        hashlib.sha256,
    ).hexdigest()


def get_api_key_credentials(
    api_key: str,
    key_preview_length: int = 12,
) -> tuple[str, str, str]:
    return api_key, api_key[:key_preview_length], hash_api_key(api_key)


def generate_api_key_credentials() -> tuple[str, str, str]:
    """
    Generate a cryptographically secure API key and API key prefix and API key hash.
    """
    api_key, api_key_prefix = generate_raw_api_key()
    api_key_hash = hash_api_key(api_key)
    return api_key, api_key_prefix, api_key_hash
