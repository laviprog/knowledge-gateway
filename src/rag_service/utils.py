import uuid
from datetime import UTC, datetime


def generate_uuid() -> str:
    """
    Generate a unique correlation ID using UUID4.
    """
    return str(uuid.uuid4())


def utc_now_iso() -> str:
    """
    Generate a UTC timestamp using ISO 8601.
    """
    return datetime.now(UTC).isoformat()
