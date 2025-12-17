"""add_user_agreements_table

Revision ID: f1a2b3c4d5e6
Revises: 0e18fdc9e742
Create Date: 2025-12-10 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = '0e18fdc9e742'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create user_agreements table for tracking user consent history."""
    # Create agreement_type enum
    agreement_type_enum = sa.Enum(
        'terms_of_service',
        'privacy_policy',
        name='agreementtype'
    )
    agreement_type_enum.create(op.get_bind(), checkfirst=True)

    # Create user_agreements table
    op.create_table(
        'user_agreements',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('agreement_type', agreement_type_enum, nullable=False),
        sa.Column('agreed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for common queries
    op.create_index(
        'ix_user_agreements_user_id',
        'user_agreements',
        ['user_id'],
        unique=False
    )
    op.create_index(
        'ix_user_agreements_agreement_type',
        'user_agreements',
        ['agreement_type'],
        unique=False
    )
    op.create_index(
        'ix_user_agreements_user_type',
        'user_agreements',
        ['user_id', 'agreement_type'],
        unique=False
    )


def downgrade() -> None:
    """Drop user_agreements table."""
    op.drop_index('ix_user_agreements_user_type', table_name='user_agreements')
    op.drop_index('ix_user_agreements_agreement_type', table_name='user_agreements')
    op.drop_index('ix_user_agreements_user_id', table_name='user_agreements')
    op.drop_table('user_agreements')

    # Drop enum type
    sa.Enum(name='agreementtype').drop(op.get_bind(), checkfirst=True)
