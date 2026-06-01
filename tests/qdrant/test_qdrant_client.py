import asyncio
from typing import TYPE_CHECKING, cast

import rag_service.qdrant.client as qdrant_client

if TYPE_CHECKING:
    from qdrant_client import AsyncQdrantClient


class FakeQdrantClient:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


def test_close_qdrant_client_closes_and_resets_shared_client(monkeypatch) -> None:
    fake_client = FakeQdrantClient()
    monkeypatch.setattr(qdrant_client, "_client", cast("AsyncQdrantClient", fake_client))

    asyncio.run(qdrant_client.close_qdrant_client())

    assert fake_client.closed is True
    assert qdrant_client._client is None
