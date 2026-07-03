from advanced_alchemy.base import UUIDAuditBase

from knowledge_gateway.database.mixins import SoftDeleteMixin


class BaseModel(SoftDeleteMixin, UUIDAuditBase):
    """Base model with UUID primary key, audit fields, and soft delete functionality."""

    __abstract__ = True

    pass
