from rag_service.documents.utils import hash_content


def test_hash_document_content_is_stable() -> None:
    assert hash_content("same content") == hash_content("same content")


def test_hash_document_content_depends_on_content() -> None:
    assert hash_content("first content") != hash_content("second content")
