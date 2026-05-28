import asyncio
from uuid import uuid4

from rag_service.documents.models import DocumentChunkModel, DocumentModel
from rag_service.documents.services import DocumentService
from rag_service.documents.utils import hash_content, split_document_content


class FakeDocumentChunkRepository:
    def __init__(self) -> None:
        self.chunks: list[DocumentChunkModel] = []

    async def add(
        self,
        chunk: DocumentChunkModel,
        auto_commit: bool,
    ) -> DocumentChunkModel:
        self.chunks.append(chunk)
        return chunk


def test_hash_document_content_is_stable() -> None:
    assert hash_content("same content") == hash_content("same content")


def test_hash_document_content_depends_on_content() -> None:
    assert hash_content("first content") != hash_content("second content")


def test_split_document_content_keeps_small_content_as_single_chunk() -> None:
    chunks = split_document_content(
        "Small paragraph",
        max_chars=100,
        overlap_chars=10,
    )

    assert chunks == ["Small paragraph"]


def test_split_document_content_splits_markdown_sections() -> None:
    content = "# Delivery\n\nDelivery terms.\n\n# Returns\n\nReturn terms."

    chunks = split_document_content(
        content,
        max_chars=30,
        overlap_chars=0,
    )

    assert chunks == ["# Delivery\n\nDelivery terms.", "# Returns\n\nReturn terms."]


def test_split_document_content_adds_overlap() -> None:
    chunks = split_document_content(
        "First paragraph with context.\n\nSecond paragraph with answer.",
        max_chars=35,
        overlap_chars=7,
    )

    assert chunks == [
        "First paragraph with context.",
        "ontext.\n\nSecond paragraph with answer.",
    ]


def test_create_chunks_for_document_updates_document_chunks_count(
    monkeypatch,
) -> None:
    monkeypatch.setattr("rag_service.documents.services.settings.DOCUMENT_CHUNK_MAX_CHARS", 30)
    monkeypatch.setattr("rag_service.documents.services.settings.DOCUMENT_CHUNK_OVERLAP_CHARS", 0)

    service = object.__new__(DocumentService)
    service.chunk_repository = FakeDocumentChunkRepository()
    document = DocumentModel(
        id=uuid4(),
        title="FAQ",
        content="# Delivery\n\nDelivery terms.\n\n# Returns\n\nReturn terms.",
        content_hash="hash",
        source=None,
        source_metadata={},
    )
    document.chunks = []

    chunks = asyncio.run(service.create_chunks_for_document(document))

    assert len(chunks) == 2
    assert document.chunks_count == 2
