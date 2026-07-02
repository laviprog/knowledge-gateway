from dataclasses import dataclass


@dataclass(frozen=True)
class VectorSearchResult:
    """
    Vector search result.
    """

    score: float
    document_id: str
    chunk_id: str
    chunk_index: int
    content: str
