from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from knowledge_gateway.database.config import sqlalchemy_config
from knowledge_gateway.documents.services import DocumentService


async def provide_document_service() -> AsyncGenerator[DocumentService, None]:
    async with DocumentService.new(config=sqlalchemy_config) as service:
        yield service


type DocumentServiceDep = Annotated[DocumentService, Depends(provide_document_service)]
