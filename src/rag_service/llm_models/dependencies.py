from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from rag_service.database.config import sqlalchemy_config
from rag_service.llm_models.services import LlmModelService


async def provide_llm_model_service() -> AsyncGenerator[LlmModelService, None]:
    async with LlmModelService.new(config=sqlalchemy_config) as service:
        yield service


type LlmModelServiceDep = Annotated[LlmModelService, Depends(provide_llm_model_service)]
