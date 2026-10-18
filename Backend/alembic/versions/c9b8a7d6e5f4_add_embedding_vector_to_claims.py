"""add embedding vector to claims

Revision ID: c9b8a7d6e5f4
Revises: 22c34a60232f
Create Date: 2026-10-18 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'c9b8a7d6e5f4'
down_revision: Union[str, Sequence[str], None] = '22c34a60232f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure vector extension is enabled in PostgreSQL
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    # Add nullable vector(768) column to preserve all existing claims and primary keys
    op.add_column(
        'claims',
        sa.Column('embedding', Vector(768), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('claims', 'embedding')
