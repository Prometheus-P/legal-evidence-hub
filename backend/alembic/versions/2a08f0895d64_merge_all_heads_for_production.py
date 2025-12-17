"""merge_all_heads_for_production

Revision ID: 2a08f0895d64
Revises: c3d4e5f6g7h8, f2a3b4c5d6e7
Create Date: 2025-12-14 15:41:09.926372

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = '2a08f0895d64'
down_revision: Union[str, Sequence[str], None] = ('c3d4e5f6g7h8', 'f2a3b4c5d6e7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
