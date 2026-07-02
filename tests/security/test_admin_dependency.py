import asyncio
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest

from knowledge_gateway.exceptions import PermissionDeniedError, UnauthorizedError
from knowledge_gateway.security import dependencies as deps
from knowledge_gateway.security.dependencies import require_admin, require_admin_session
from knowledge_gateway.users.models import Role


class FakeApiKeyService:
    def __init__(self, api_key_model: SimpleNamespace | None = None):
        self.api_key_model = api_key_model

    async def validate_api_key(self, api_key: str) -> SimpleNamespace | None:
        return self.api_key_model


class FakeUserService:
    def __init__(self, user: SimpleNamespace | None = None):
        self.user = user
        self.requested_id: Any = None

    async def get_active_or_none(self, user_id) -> SimpleNamespace | None:
        self.requested_id = user_id
        return self.user


def as_dependency(value: object) -> Any:
    return value


def test_require_admin_resolves_session_first(monkeypatch: pytest.MonkeyPatch) -> None:
    user_id = uuid4()
    monkeypatch.setattr(deps, "resolve_session_user_id", lambda token: _async(user_id))
    user_service = FakeUserService(SimpleNamespace(id=user_id, role=Role.ADMIN))

    result = asyncio.run(
        require_admin(
            api_key_service=as_dependency(FakeApiKeyService()),
            user_service=as_dependency(user_service),
            authorization=None,
            session_token="session-token",
        )
    )

    assert result.user_id == user_id
    assert user_service.requested_id == user_id


def test_require_admin_falls_back_to_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(deps, "resolve_session_user_id", lambda token: _async(None))
    user_id = uuid4()
    api_key_model = SimpleNamespace(id=uuid4(), user=SimpleNamespace(id=user_id, role=Role.ADMIN))

    result = asyncio.run(
        require_admin(
            api_key_service=as_dependency(FakeApiKeyService(api_key_model)),
            user_service=as_dependency(FakeUserService()),
            authorization="Bearer secret",
            session_token=None,
        )
    )

    assert result.user_id == user_id


def test_require_admin_rejects_non_admin_session_without_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(deps, "resolve_session_user_id", lambda token: _async(uuid4()))
    user_service = FakeUserService(SimpleNamespace(id=uuid4(), role=Role.USER))

    with pytest.raises(UnauthorizedError):
        asyncio.run(
            require_admin(
                api_key_service=as_dependency(FakeApiKeyService()),
                user_service=as_dependency(user_service),
                authorization=None,
                session_token="session-token",
            )
        )


def test_require_admin_rejects_non_admin_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(deps, "resolve_session_user_id", lambda token: _async(None))
    api_key_model = SimpleNamespace(id=uuid4(), user=SimpleNamespace(id=uuid4(), role=Role.USER))

    with pytest.raises(PermissionDeniedError):
        asyncio.run(
            require_admin(
                api_key_service=as_dependency(FakeApiKeyService(api_key_model)),
                user_service=as_dependency(FakeUserService()),
                authorization="Bearer secret",
                session_token=None,
            )
        )


def test_require_admin_session_rejects_missing_cookie(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(deps, "resolve_session_user_id", lambda token: _async(None))

    with pytest.raises(UnauthorizedError):
        asyncio.run(
            require_admin_session(
                user_service=as_dependency(FakeUserService()),
                session_token=None,
            )
        )


async def _async(value):
    return value
