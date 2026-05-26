import uuid
from datetime import UTC, datetime


def generate_uuid() -> str:
    """
    Generate a unique correlation ID using UUID4.
    """
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """
    Generate a UTC datetime object.
    """
    return datetime.now(UTC)


def utc_now_iso() -> str:
    """
    Generate a UTC timestamp using ISO 8601.
    """
    return utc_now().isoformat()
