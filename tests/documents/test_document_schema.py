from uuid import uuid4

import pytest
from pydantic import ValidationError

from knowledge_gateway.documents.schema import DocumentCreate


def test_document_create_accepts_minimal_payload() -> None:
    knowledge_base_id = uuid4()
    schema = DocumentCreate(knowledge_base_id=knowledge_base_id, title="FAQ", content="Answer text")

    assert schema.knowledge_base_id == knowledge_base_id
    assert schema.title == "FAQ"
    assert schema.content == "Answer text"
    assert schema.source is None
    assert schema.source_metadata == {}


def test_document_create_rejects_empty_content() -> None:
    with pytest.raises(ValidationError):
        DocumentCreate(knowledge_base_id=uuid4(), title="FAQ", content="")
