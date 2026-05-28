import asyncio
from uuid import uuid4

from rag_service.documents.models import DocumentChunkModel, DocumentIndexStatus, DocumentModel
from rag_service.documents.services import DocumentService
from rag_service.documents.utils import hash_content, split_document_content


class FakeDocumentChunkRepository:
    def __init__(self, chunks: list[DocumentChunkModel] | None = None) -> None:
        self.chunks = chunks or []
        self.updated_chunks: list[DocumentChunkModel] = []

    async def add(
        self,
        chunk: DocumentChunkModel,
        auto_commit: bool,
    ) -> DocumentChunkModel:
        self.chunks.append(chunk)
        return chunk

    async def update(
        self,
        chunk: DocumentChunkModel,
        auto_commit: bool,
    ) -> DocumentChunkModel:
        self.updated_chunks.append(chunk)
        return chunk

    async def list(self, *filters) -> list[DocumentChunkModel]:
        return self.chunks


class FakeDocumentRepository:
    def __init__(self, document: DocumentModel) -> None:
        self.document = document
        self.updated_documents: list[DocumentModel] = []

    async def get_one_or_none(self, *filters, **kwargs) -> DocumentModel | None:
        return self.document

    async def update(
        self,
        document: DocumentModel,
        auto_commit: bool,
    ) -> DocumentModel:
        self.updated_documents.append(document)
        return document


class FakeEmbeddingClient:
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[float(index), 0.1] for index, _ in enumerate(texts)]


class FakeVectorStore:
    def __init__(self) -> None:
        self.chunks: list[DocumentChunkModel] = []
        self.embeddings: list[list[float]] = []

    async def upsert_chunks(
        self,
        chunks: list[DocumentChunkModel],
        embeddings: list[list[float]],
    ) -> list[str]:
        self.chunks = chunks
        self.embeddings = embeddings
        return [f"point-{index}" for index, _ in enumerate(chunks)]


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


def test_index_chunks_updates_qdrant_point_ids() -> None:
    service = object.__new__(DocumentService)
    service.chunk_repository = FakeDocumentChunkRepository()
    service.embedding_client = FakeEmbeddingClient()
    service.vector_store = FakeVectorStore()

    chunks = [
        DocumentChunkModel(
            id=uuid4(),
            document_id=uuid4(),
            chunk_index=0,
            content="First chunk",
            content_hash="first",
        ),
        DocumentChunkModel(
            id=uuid4(),
            document_id=uuid4(),
            chunk_index=1,
            content="Second chunk",
            content_hash="second",
        ),
    ]

    asyncio.run(service.index_chunks(chunks))

    assert [chunk.qdrant_point_id for chunk in chunks] == ["point-0", "point-1"]
    assert len(service.chunk_repository.updated_chunks) == 2
    assert service.vector_store.embeddings == [[0.0, 0.1], [1.0, 0.1]]


def test_index_document_updates_document_status() -> None:
    document_id = uuid4()
    document = DocumentModel(
        id=document_id,
        title="FAQ",
        content="FAQ content",
        content_hash="hash",
        source=None,
        source_metadata={},
    )
    chunk = DocumentChunkModel(
        id=uuid4(),
        document_id=document_id,
        chunk_index=0,
        content="First chunk",
        content_hash="first",
    )

    service = object.__new__(DocumentService)
    service._repository_instance = FakeDocumentRepository(document)
    service.chunk_repository = FakeDocumentChunkRepository([chunk])
    service.embedding_client = FakeEmbeddingClient()
    service.vector_store = FakeVectorStore()

    asyncio.run(service.index_document(document_id))

    assert document.index_status == DocumentIndexStatus.INDEXED
    assert document.index_error is None
    assert document.indexed_at is not None
    assert chunk.qdrant_point_id == "point-0"
