from datetime import UTC, datetime

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """
    Base schema with common configurations and methods.
    """

    model_config = {"from_attributes": True}

    def to_dict(self, exclude_none: bool = True) -> dict:
        return self.model_dump(exclude_none=exclude_none)


class HealthCheck(BaseModel):
    """
    Health check schema to indicate service status and timestamp.
    """

    status: str = "ok"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
