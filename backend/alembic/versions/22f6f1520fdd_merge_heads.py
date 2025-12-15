"""merge heads

Revision ID: 22f6f1520fdd
Revises: 012a_auto_extract, 4b10g2907f86
Create Date: 2025-12-15 14:04:47.587757

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = '22f6f1520fdd'
down_revision: Union[str, Sequence[str], None] = ('012a_auto_extract', '4b10g2907f86')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
