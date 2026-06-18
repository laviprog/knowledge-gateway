import os

import pytest

os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "rag_service_test")
os.environ.setdefault("POSTGRES_USER", "rag_service_test")
os.environ.setdefault("POSTGRES_PASSWORD", "rag_service_test")
os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
os.environ.setdefault("QDRANT_API_KEY", "test")
os.environ.setdefault("LLM_BASE_URL", "http://localhost:11434/v1")
os.environ.setdefault("LLM_API_KEY", "test")
os.environ.setdefault("LLM_EMBEDDING_MODEL", "embeddinggemma")
os.environ.setdefault("API_KEY_PEPPER", "test-pepper-value-for-tests-only")


@pytest.fixture(params=["asyncio"])
def anyio_backend(request: pytest.FixtureRequest) -> str:
    return request.param  # type: ignore[return-value]
