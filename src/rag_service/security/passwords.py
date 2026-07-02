from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """
    Hash a plaintext password with Argon2 for storage at rest.
    """
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a plaintext password against a stored Argon2 hash.

    Returns False on any mismatch or malformed hash rather than raising, so callers can treat
    authentication as a simple boolean.
    """
    try:
        return _hasher.verify(password_hash, password)
    except (Argon2Error, ValueError):
        return False
