import os

import pytest

os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "knowledge_gateway_test")
os.environ.setdefault("POSTGRES_USER", "knowledge_gateway_test")
os.environ.setdefault("POSTGRES_PASSWORD", "knowledge_gateway_test")
os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
os.environ.setdefault("QDRANT_API_KEY", "test")
os.environ.setdefault("API_KEY_PEPPER", "test-pepper-value-for-tests-only")
os.environ.setdefault("PROVIDER_SECRET_KEY", "test-provider-secret-for-tests-only")


@pytest.fixture(params=["asyncio"])
def anyio_backend(request: pytest.FixtureRequest) -> str:
    return request.param  # type: ignore[return-value]
