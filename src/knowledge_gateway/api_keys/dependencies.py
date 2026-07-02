from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from knowledge_gateway.database.config import sqlalchemy_config

from .services import ApiKeyService


async def provide_api_key_service() -> AsyncGenerator[ApiKeyService, None]:
    async with ApiKeyService.new(config=sqlalchemy_config) as service:
        yield service


type ApiKeyServiceDep = Annotated[ApiKeyService, Depends(provide_api_key_service)]
