import pytest

import rag_service.security.encryption as encryption
from rag_service.config import settings
from rag_service.security.encryption import (
    ProviderSecretError,
    decrypt_secret,
    encrypt_secret,
)


def test_encrypt_decrypt_round_trip() -> None:
    token = encrypt_secret("super-secret-key")

    assert token != "super-secret-key"
    assert decrypt_secret(token) == "super-secret-key"


def test_encrypt_is_non_deterministic() -> None:
    # Fernet embeds a random IV, so the same plaintext encrypts to different tokens.
    assert encrypt_secret("value") != encrypt_secret("value")


def test_encrypt_raises_without_secret_key(monkeypatch) -> None:
    monkeypatch.setattr(encryption, "_fernet", None)
    monkeypatch.setattr(settings, "PROVIDER_SECRET_KEY", None)

    with pytest.raises(ProviderSecretError):
        encrypt_secret("value")
