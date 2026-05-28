from uuid import UUID

from rag_service.database.config import sqlalchemy_config
from rag_service.documents.services import DocumentService
from rag_service.log_config import get_log

log = get_log(__name__)


async def index_document(document_id: UUID) -> None:
    """
    Index a document in the background.
    """
    try:
        async with DocumentService.new(config=sqlalchemy_config) as service:
            await service.index_document(document_id)
    except Exception:
        log.exception("Document indexing failed", document_id=str(document_id))
