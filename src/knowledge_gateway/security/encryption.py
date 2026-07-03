import base64
import hashlib

from cryptography.fernet import Fernet
from sqlalchemy import String
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.types import TypeDecorator

from knowledge_gateway.config import settings

_fernet: Fernet | None = None


class ProviderSecretError(RuntimeError):
    """
    Raised when an encrypted value must be processed but ``PROVIDER_SECRET_KEY`` is unset.
    """


def _get_fernet() -> Fernet:
    """
    Return a process-wide Fernet built from ``PROVIDER_SECRET_KEY``.

    A valid 32-byte urlsafe key is derived from the configured secret via SHA-256, so the
    secret itself can be any string (mirroring ``API_KEY_PEPPER``).
    """
    global _fernet
    if _fernet is None:
        if not settings.PROVIDER_SECRET_KEY:
            raise ProviderSecretError(
                "PROVIDER_SECRET_KEY must be set to store or read encrypted provider secrets."
            )
        derived = base64.urlsafe_b64encode(
            hashlib.sha256(settings.PROVIDER_SECRET_KEY.encode()).digest()
        )
        _fernet = Fernet(derived)

    return _fernet


def encrypt_secret(value: str) -> str:
    """
    Encrypt a plaintext secret for storage.
    """
    return _get_fernet().encrypt(value.encode()).decode()


def decrypt_secret(token: str) -> str:
    """
    Decrypt a stored secret back to plaintext.
    """
    return _get_fernet().decrypt(token.encode()).decode()


class EncryptedString(TypeDecorator):
    """
    Transparently encrypts string values at rest with Fernet (AES-128-CBC + HMAC).

    Stored as opaque ciphertext text; ``None`` passes through untouched so optional secret
    columns stay nullable.
    """

    impl = String
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect: Dialect) -> str | None:
        if value is None:
            return None
        return encrypt_secret(value)

    def process_result_value(self, value: str | None, dialect: Dialect) -> str | None:
        if value is None:
            return None
        return decrypt_secret(value)
