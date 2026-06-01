import asyncio
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest

from rag_service.exceptions import PermissionDeniedError, UnauthorizedError
from rag_service.security.dependencies import require_admin_key, require_user_key
from rag_service.users.models import Role


class FakeApiKeyService:
    def __init__(self, api_key_model: SimpleNamespace | None = None):
        self.api_key_model = api_key_model
        self.validated_api_key: str | None = None

    async def validate_api_key(self, api_key: str) -> SimpleNamespace | None:
        self.validated_api_key = api_key
        return self.api_key_model


def as_dependency(value: object) -> Any:
    return value


def test_require_admin_key_returns_user_id_for_admin_key() -> None:
    user_id = uuid4()
    api_key_id = uuid4()
    api_key_model = SimpleNamespace(
        id=api_key_id,
        user=SimpleNamespace(id=user_id, role=Role.ADMIN),
    )
    api_key_service = FakeApiKeyService(api_key_model)

    result = asyncio.run(
        require_admin_key(
            api_key_service=as_dependency(api_key_service),
            authorization="Bearer secret",
        )
    )

    assert result.user_id == user_id
    assert result.api_key_id == api_key_id
    assert api_key_service.validated_api_key == "secret"


def test_require_user_key_returns_auth_context_for_user_key() -> None:
    user_id = uuid4()
    api_key_id = uuid4()
    api_key_model = SimpleNamespace(id=api_key_id, user=SimpleNamespace(id=user_id, role=Role.USER))
    api_key_service = FakeApiKeyService(api_key_model)

    result = asyncio.run(
        require_user_key(
            api_key_service=as_dependency(api_key_service),
            authorization="Bearer secret",
        )
    )

    assert result.user_id == user_id
    assert result.api_key_id == api_key_id


def test_require_admin_key_rejects_missing_authorization_header() -> None:
    api_key_service = FakeApiKeyService()

    with pytest.raises(UnauthorizedError):
        asyncio.run(
            require_admin_key(
                api_key_service=as_dependency(api_key_service),
                authorization=None,
            )
        )

    assert api_key_service.validated_api_key is None


def test_require_admin_key_rejects_non_admin_key() -> None:
    user_id = uuid4()
    api_key_model = SimpleNamespace(id=uuid4(), user=SimpleNamespace(id=user_id, role=Role.USER))
    api_key_service = FakeApiKeyService(api_key_model)

    with pytest.raises(PermissionDeniedError):
        asyncio.run(
            require_admin_key(
                api_key_service=as_dependency(api_key_service),
                authorization="Bearer secret",
            )
        )
