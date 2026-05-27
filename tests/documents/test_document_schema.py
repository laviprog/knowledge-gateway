import pytest
from pydantic import ValidationError

from rag_service.documents.schema import DocumentCreate


def test_document_create_accepts_minimal_payload() -> None:
    schema = DocumentCreate(title="FAQ", content="Answer text")

    assert schema.title == "FAQ"
    assert schema.content == "Answer text"
    assert schema.source is None
    assert schema.source_metadata == {}


def test_document_create_rejects_empty_content() -> None:
    with pytest.raises(ValidationError):
        DocumentCreate(title="FAQ", content="")
