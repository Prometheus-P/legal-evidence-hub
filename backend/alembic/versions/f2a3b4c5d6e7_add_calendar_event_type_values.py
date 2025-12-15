"""add calendar event type enum values

Revision ID: f2a3b4c5d6e7
Revises: f1a2b3c4d5e6
Create Date: 2025-12-12

Ensure calendareventtype includes all values used by the application.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2a3b4c5d6e7'
down_revision: Union[str, Sequence[str], None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ENUM_NAME = 'calendareventtype'
ENUM_VALUES = ['court', 'meeting', 'deadline', 'internal', 'other']


def _enum_exists(connection, enum_name: str) -> bool:
    result = connection.execute(
        sa.text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = :name)"),
        {'name': enum_name},
    )
    return bool(result.scalar())


def upgrade() -> None:
    connection = op.get_bind()

    if not _enum_exists(connection, ENUM_NAME):
        return

    existing_values = connection.execute(
        sa.text(f"SELECT unnest(enum_range(NULL::{ENUM_NAME}))::text")
    )
    existing = {row[0] for row in existing_values}

    for value in ENUM_VALUES:
        if value not in existing:
            op.execute(f"ALTER TYPE {ENUM_NAME} ADD VALUE IF NOT EXISTS '{value}'")


def downgrade() -> None:
    """Enum values cannot be removed safely; no downgrade."""
    pass
