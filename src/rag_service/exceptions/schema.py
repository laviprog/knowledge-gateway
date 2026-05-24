from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: str
    detail: str
    timestamp: str


class ValidationErrorResponse(BaseModel):
    code: str
    detail: list[dict[str, Any]]
    timestamp: str
