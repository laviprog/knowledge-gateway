from datetime import UTC, datetime

from sqlalchemy.orm import Mapped


class SoftDeleteMixin:
    """
    Mixin to add soft delete functionality to SQLAlchemy models.
    """

    deleted_at: Mapped[datetime | None]

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(UTC)

    def restore(self) -> None:
        self.deleted_at = None
