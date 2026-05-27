"""Create document models

Revision ID: 1a2b3c4d5e6f
Revises: 8cf49b9b8fa4
Create Date: 2026-05-27 19:45:00.000000

"""

from collections.abc import Sequence

import advanced_alchemy
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "1a2b3c4d5e6f"
down_revision: str | Sequence[str] | None = "8cf49b9b8fa4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "documents",
        sa.Column("id", advanced_alchemy.types.guid.GUID(length=16), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("source", sa.String(length=512), nullable=True),
        sa.Column("source_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "deleted_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=True
        ),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False
        ),
        sa.Column(
            "updated_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_documents")),
    )
    op.create_index(op.f("ix_documents_content_hash"), "documents", ["content_hash"], unique=False)

    op.create_table(
        "document_chunks",
        sa.Column("id", advanced_alchemy.types.guid.GUID(length=16), nullable=False),
        sa.Column("document_id", advanced_alchemy.types.guid.GUID(length=16), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("qdrant_point_id", sa.String(length=64), nullable=True),
        sa.Column(
            "deleted_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=True
        ),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False
        ),
        sa.Column(
            "updated_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["document_id"], ["documents.id"], name=op.f("fk_document_chunks_document_id_documents")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_chunks")),
        sa.UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_document_chunks_document_id_chunk_index",
        ),
    )
    op.create_index(
        op.f("ix_document_chunks_content_hash"),
        "document_chunks",
        ["content_hash"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_chunks_document_id"),
        "document_chunks",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_document_chunks_qdrant_point_id"),
        "document_chunks",
        ["qdrant_point_id"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_document_chunks_qdrant_point_id"), table_name="document_chunks")
    op.drop_index(op.f("ix_document_chunks_document_id"), table_name="document_chunks")
    op.drop_index(op.f("ix_document_chunks_content_hash"), table_name="document_chunks")
    op.drop_table("document_chunks")
    op.drop_index(op.f("ix_documents_content_hash"), table_name="documents")
    op.drop_table("documents")
