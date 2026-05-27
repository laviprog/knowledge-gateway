import hashlib


def hash_content(content: str) -> str:
    """
    Build a stable content hash.
    """
    return hashlib.sha256(content.encode()).hexdigest()
