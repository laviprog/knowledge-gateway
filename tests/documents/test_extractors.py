import asyncio
from io import BytesIO

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from rag_service.config import settings
from rag_service.documents.extractors import extract_document_from_upload
from rag_service.exceptions import BadRequestError


def make_upload_file(
    filename: str,
    content: bytes,
    content_type: str = "text/plain",
) -> UploadFile:
    return UploadFile(
        file=BytesIO(content),
        filename=filename,
        headers=Headers({"content-type": content_type}),
    )


def test_extract_document_from_upload_extracts_text_file() -> None:
    file = make_upload_file("faq.txt", b"Hello from file")

    extracted_document = asyncio.run(extract_document_from_upload(file))

    assert extracted_document.title == "faq.txt"
    assert extracted_document.content == "Hello from file"
    assert extracted_document.source == "faq.txt"
    assert extracted_document.source_metadata["source_type"] == "file"
    assert extracted_document.source_metadata["filename"] == "faq.txt"
    assert extracted_document.source_metadata["parser"] == "markitdown"
    assert extracted_document.source_metadata["size"] == len(b"Hello from file")


def test_extract_document_from_upload_rejects_unsupported_file_type() -> None:
    file = make_upload_file("archive.zip", b"content")

    with pytest.raises(BadRequestError, match="Unsupported file type"):
        asyncio.run(extract_document_from_upload(file))


def test_extract_document_from_upload_rejects_empty_file() -> None:
    file = make_upload_file("empty.txt", b"")

    with pytest.raises(BadRequestError, match="File is empty"):
        asyncio.run(extract_document_from_upload(file))


def test_extract_document_from_upload_rejects_large_file(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "DOCUMENT_UPLOAD_MAX_BYTES", 3)
    file = make_upload_file("large.txt", b"large")

    with pytest.raises(BadRequestError, match="File is too large"):
        asyncio.run(extract_document_from_upload(file))
