"""merge_all_heads

Revision ID: 9fdb562bff2a
Revises: b2c3d4e5f6g7, b5c6d7e8f9a0, c7e5f1a2b3c4
Create Date: 2025-12-08 12:13:01.975495

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = '9fdb562bff2a'
down_revision: Union[str, Sequence[str], None] = ('b2c3d4e5f6g7', 'b5c6d7e8f9a0', 'c7e5f1a2b3c4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
