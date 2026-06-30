import asyncio
from uuid import uuid4

from rag_service.documents.models import DocumentChunkModel, DocumentIndexStatus, DocumentModel
from rag_service.documents.services import DocumentService
from rag_service.documents.utils import hash_content, split_document_content
from rag_service.embedding_models.models import EmbeddingModel
from rag_service.knowledge_bases.models import KnowledgeBaseModel
from rag_service.qdrant.vector_store import VectorSearchResult


def build_knowledge_base() -> KnowledgeBaseModel:
    embedding_model = EmbeddingModel(
        id=uuid4(),
        public_id="emb-default",
        provider_model="bge-m3",
        dimension=None,
        collection_name="kb_emb_default",
        provider_id=uuid4(),
    )
    knowledge_base = KnowledgeBaseModel(
        id=uuid4(),
        public_id="default",
        name="Default",
        embedding_model_id=embedding_model.id,
    )
    knowledge_base.embedding_model = embedding_model
    return knowledge_base


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
    def __init__(self) -> None:
        self.texts: list[str] = []

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.texts = texts
        return [[float(index), 0.1] for index, _ in enumerate(texts)]


class FakeVectorStore:
    def __init__(self) -> None:
        self.chunks: list[DocumentChunkModel] = []
        self.embeddings: list[list[float]] = []
        self.query_embedding: list[float] | None = None
        self.limit: int | None = None
        self.collection_name: str | None = None
        self.knowledge_base_id: str | None = None

    async def upsert_chunks(
        self,
        collection_name: str,
        knowledge_base_id: str,
        chunks: list[DocumentChunkModel],
        embeddings: list[list[float]],
    ) -> list[str]:
        self.collection_name = collection_name
        self.knowledge_base_id = knowledge_base_id
        self.chunks = chunks
        self.embeddings = embeddings
        return [f"point-{index}" for index, _ in enumerate(chunks)]

    async def search(
        self,
        collection_name: str,
        knowledge_base_id: str,
        query_embedding: list[float],
        limit: int,
    ) -> list[VectorSearchResult]:
        self.collection_name = collection_name
        self.knowledge_base_id = knowledge_base_id
        self.query_embedding = query_embedding
        self.limit = limit
        return [
            VectorSearchResult(
                score=0.9,
                document_id=str(uuid4()),
                chunk_id=str(uuid4()),
                chunk_index=1,
                content="Matching content",
            )
        ]


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
    knowledge_base = build_knowledge_base()
    embedding_client = FakeEmbeddingClient()
    service = object.__new__(DocumentService)
    service.chunk_repository = FakeDocumentChunkRepository()
    service.vector_store = FakeVectorStore()
    service._embedding_client_for = lambda embedding_model: embedding_client

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

    asyncio.run(service.index_chunks(knowledge_base, chunks))

    assert [chunk.qdrant_point_id for chunk in chunks] == ["point-0", "point-1"]
    assert len(service.chunk_repository.updated_chunks) == 2
    assert service.vector_store.embeddings == [[0.0, 0.1], [1.0, 0.1]]
    assert service.vector_store.collection_name == "kb_emb_default"
    assert service.vector_store.knowledge_base_id == str(knowledge_base.id)


def test_index_document_updates_document_status() -> None:
    document_id = uuid4()
    knowledge_base = build_knowledge_base()
    document = DocumentModel(
        id=document_id,
        knowledge_base_id=knowledge_base.id,
        title="FAQ",
        content="FAQ content",
        content_hash="hash",
        source=None,
        source_metadata={},
    )
    document.knowledge_base = knowledge_base
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
    service.vector_store = FakeVectorStore()
    service._embedding_client_for = lambda embedding_model: FakeEmbeddingClient()

    asyncio.run(service.index_document(document_id))

    assert document.index_status == DocumentIndexStatus.INDEXED
    assert document.index_error is None
    assert document.indexed_at is not None
    assert chunk.qdrant_point_id == "point-0"


def test_search_documents_embeds_query_and_searches_vector_store() -> None:
    knowledge_base = build_knowledge_base()
    embedding_client = FakeEmbeddingClient()
    service = object.__new__(DocumentService)
    service.vector_store = FakeVectorStore()
    service._embedding_client_for = lambda embedding_model: embedding_client

    results = asyncio.run(
        service.search_documents(query="return policy", limit=3, knowledge_base=knowledge_base)
    )

    assert embedding_client.texts == ["return policy"]
    assert service.vector_store.query_embedding == [0.0, 0.1]
    assert service.vector_store.limit == 3
    assert service.vector_store.collection_name == "kb_emb_default"
    assert service.vector_store.knowledge_base_id == str(knowledge_base.id)
    assert len(results) == 1
    assert results[0].content == "Matching content"


def test_search_documents_without_knowledge_base_returns_empty() -> None:
    service = object.__new__(DocumentService)
    service.vector_store = FakeVectorStore()

    results = asyncio.run(service.search_documents(query="anything", limit=3, knowledge_base=None))

    assert results == []
    assert service.vector_store.query_embedding is None
