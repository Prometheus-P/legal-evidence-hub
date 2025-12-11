"""add_detective_earnings_table

Revision ID: 7f318fded1a1
Revises: f1a2b3c4d5e6
Create Date: 2025-12-11 10:49:14.619157

009-mvp-gap-closure - US11 (FR-040)
Detective earnings table for tracking detective payments
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f318fded1a1'
down_revision: Union[str, Sequence[str], None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create detective_earnings table."""
    # Create earnings_status enum
    earnings_status_enum = sa.Enum('pending', 'paid', name='earningsstatus')
    earnings_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'detective_earnings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('detective_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('case_id', sa.String(36), sa.ForeignKey('cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('status', earnings_status_enum, nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('paid_at', sa.DateTime, nullable=True),
    )

    # Create indexes for common queries
    op.create_index('ix_detective_earnings_detective_id', 'detective_earnings', ['detective_id'])
    op.create_index('ix_detective_earnings_case_id', 'detective_earnings', ['case_id'])
    op.create_index('ix_detective_earnings_status', 'detective_earnings', ['status'])


def downgrade() -> None:
    """Drop detective_earnings table."""
    op.drop_index('ix_detective_earnings_status', 'detective_earnings')
    op.drop_index('ix_detective_earnings_case_id', 'detective_earnings')
    op.drop_index('ix_detective_earnings_detective_id', 'detective_earnings')
    op.drop_table('detective_earnings')

    # Drop enum type
    earnings_status_enum = sa.Enum('pending', 'paid', name='earningsstatus')
    earnings_status_enum.drop(op.get_bind(), checkfirst=True)
