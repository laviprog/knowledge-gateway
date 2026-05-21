import uuid


def generate_uuid() -> str:
    """
    Generate a unique correlation ID using UUID4.
    """
    return str(uuid.uuid4())
