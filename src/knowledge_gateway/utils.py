import uuid
from datetime import UTC, datetime

from knowledge_gateway.config import settings


def is_dev_env() -> bool:
    """
    Check if the current environment is development.
    """
    return settings.ENV == "dev"


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
