from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from fastapi import UploadFile
from markitdown import MarkItDown

from rag_service.config import settings
from rag_service.exceptions import BadRequestError

ALLOWED_FILE_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}
MARKITDOWN_PARSER_NAME = "markitdown"


@dataclass(frozen=True)
class ExtractedDocument:
    """
    Extracted document content and source metadata.
    """

    title: str
    content: str
    source: str
    source_metadata: dict


def get_file_extension(filename: str) -> str:
    """
    Return normalized file extension.
    """
    return Path(filename).suffix.lower()


async def extract_document_from_upload(file: UploadFile) -> ExtractedDocument:
    """
    Extract markdown content from an uploaded file.
    """
    filename = file.filename or "uploaded_document"
    file_extension = get_file_extension(filename)

    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        raise BadRequestError("Unsupported file type")

    content_bytes = await file.read(settings.DOCUMENT_UPLOAD_MAX_BYTES + 1)
    if len(content_bytes) > settings.DOCUMENT_UPLOAD_MAX_BYTES:
        raise BadRequestError("File is too large")

    if not content_bytes:
        raise BadRequestError("File is empty")

    try:
        result = MarkItDown(enable_plugins=False).convert(
            BytesIO(content_bytes),
            file_extension=file_extension,
        )
    except Exception as exc:
        raise BadRequestError("Could not extract document content") from exc

    content = result.markdown.strip()
    if not content:
        raise BadRequestError("Extracted document content is empty")

    return ExtractedDocument(
        title=filename,
        content=content,
        source=filename,
        source_metadata={
            "source_type": "file",
            "filename": filename,
            "content_type": file.content_type,
            "size": len(content_bytes),
            "parser": MARKITDOWN_PARSER_NAME,
        },
    )
