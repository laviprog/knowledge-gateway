from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from rag_service.database.config import sqlalchemy_config
from rag_service.providers.services import ProviderService


async def provide_provider_service() -> AsyncGenerator[ProviderService, None]:
    async with ProviderService.new(config=sqlalchemy_config) as service:
        yield service


type ProviderServiceDep = Annotated[ProviderService, Depends(provide_provider_service)]
