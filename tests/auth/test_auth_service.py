from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest

from rag_service.auth.services import AuthService
from rag_service.exceptions import UnauthorizedError
from rag_service.security.passwords import hash_password
from rag_service.users.models import Role


class FakeUserService:
    def __init__(self, user: SimpleNamespace | None) -> None:
        self.user = user

    async def get_active_by_name_or_none(self, name: str) -> SimpleNamespace | None:
        return self.user


def _auth_service(user: SimpleNamespace | None) -> AuthService:
    return AuthService(user_service=_as_service(FakeUserService(user)))


def _as_service(value: object) -> Any:
    return value


def _admin(password: str | None = "secret") -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(),
        name="admin",
        role=Role.ADMIN,
        password_hash=hash_password(password) if password is not None else None,
    )


@pytest.mark.anyio
async def test_authenticate_returns_admin_on_valid_credentials() -> None:
    admin = _admin()
    service = _auth_service(admin)

    result = await service.authenticate("admin", "secret")

    assert result is admin


@pytest.mark.anyio
async def test_authenticate_rejects_wrong_password() -> None:
    service = _auth_service(_admin())

    with pytest.raises(UnauthorizedError):
        await service.authenticate("admin", "wrong")


@pytest.mark.anyio
async def test_authenticate_rejects_unknown_user() -> None:
    service = _auth_service(None)

    with pytest.raises(UnauthorizedError):
        await service.authenticate("ghost", "secret")


@pytest.mark.anyio
async def test_authenticate_rejects_non_admin() -> None:
    user = _admin()
    user.role = Role.USER
    service = _auth_service(user)

    with pytest.raises(UnauthorizedError):
        await service.authenticate("admin", "secret")


@pytest.mark.anyio
async def test_authenticate_rejects_admin_without_password() -> None:
    service = _auth_service(_admin(password=None))

    with pytest.raises(UnauthorizedError):
        await service.authenticate("admin", "secret")
