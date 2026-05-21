from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
    timestamp: str
