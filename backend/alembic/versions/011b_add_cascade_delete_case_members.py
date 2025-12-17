"""add_cascade_delete_case_members

Revision ID: 011b_cascade_delete
Revises: 22f6f1520fdd
Create Date: 2025-12-15

Add ON DELETE CASCADE to case_members.case_id foreign key
so that deleting a case automatically deletes its members.
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '011b_cascade_delete'
down_revision: Union[str, Sequence[str], None] = '22f6f1520fdd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add ON DELETE CASCADE to case_members.case_id FK."""
    # Drop the existing foreign key constraint
    op.drop_constraint('case_members_case_id_fkey', 'case_members', type_='foreignkey')

    # Recreate with ON DELETE CASCADE
    op.create_foreign_key(
        'case_members_case_id_fkey',
        'case_members',
        'cases',
        ['case_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Remove ON DELETE CASCADE from case_members.case_id FK."""
    # Drop the cascade foreign key constraint
    op.drop_constraint('case_members_case_id_fkey', 'case_members', type_='foreignkey')

    # Recreate without ON DELETE CASCADE
    op.create_foreign_key(
        'case_members_case_id_fkey',
        'case_members',
        'cases',
        ['case_id'],
        ['id']
    )
