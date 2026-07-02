from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from knowledge_gateway.database.config import sqlalchemy_config
from knowledge_gateway.knowledge_bases.services import KnowledgeBaseService


async def provide_knowledge_base_service() -> AsyncGenerator[KnowledgeBaseService, None]:
    async with KnowledgeBaseService.new(config=sqlalchemy_config) as service:
        yield service


type KnowledgeBaseServiceDep = Annotated[
    KnowledgeBaseService, Depends(provide_knowledge_base_service)
]
