"""merge_heads_before_indexes

Revision ID: a1b2c3d4e5f7
Revises: 7b87c05c5796, 7f318fded1a1
Create Date: 2025-12-12

Merge two parallel branches before adding performance indexes.
"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f7'
down_revision: Union[str, Sequence[str], None] = ('7b87c05c5796', '7f318fded1a1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge heads - no schema changes."""
    pass


def downgrade() -> None:
    """Merge heads - no schema changes."""
    pass
