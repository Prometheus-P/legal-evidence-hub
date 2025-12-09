"""merge_heads

Revision ID: 4821242f228f
Revises: d1e2f3g4h5i6, e9f0a1b2c3d4
Create Date: 2025-12-09 14:33:40.951863

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4821242f228f'
down_revision: Union[str, Sequence[str], None] = ('d1e2f3g4h5i6', 'e9f0a1b2c3d4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
