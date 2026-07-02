from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from knowledge_gateway.database.config import sqlalchemy_config
from knowledge_gateway.embedding_models.services import EmbeddingModelService


async def provide_embedding_model_service() -> AsyncGenerator[EmbeddingModelService, None]:
    async with EmbeddingModelService.new(config=sqlalchemy_config) as service:
        yield service


type EmbeddingModelServiceDep = Annotated[
    EmbeddingModelService, Depends(provide_embedding_model_service)
]
