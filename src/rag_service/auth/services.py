from rag_service.exceptions import UnauthorizedError
from rag_service.security.passwords import verify_password
from rag_service.users.models import Role, UserModel
from rag_service.users.services import UserService


class AuthService:
    """Interactive (admin panel) authentication."""

    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    async def authenticate(self, name: str, password: str) -> UserModel:
        """
        Verify admin credentials and return the user, or raise UnauthorizedError.

        Only admins with a password set can log in interactively. The error is intentionally
        generic to avoid leaking whether a name exists.
        """
        user = await self.user_service.get_active_by_name_or_none(name)

        if (
            user is None
            or user.role != Role.ADMIN
            or user.password_hash is None
            or not verify_password(password, user.password_hash)
        ):
            raise UnauthorizedError("Invalid credentials")

        return user
