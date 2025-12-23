"""add consultation tables

Revision ID: consult_001
Revises: 724a7e3ccf5e
Create Date: 2025-12-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'consult_001'
down_revision: Union[str, Sequence[str], None] = '724a7e3ccf5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create consultation tables."""
    # Create consultations table
    op.create_table(
        'consultations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('case_id', sa.String(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('time', sa.Time(), nullable=True),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_consultations_case_id', 'consultations', ['case_id'])
    op.create_index('ix_consultations_date', 'consultations', ['date'])

    # Create consultation_participants table
    op.create_table(
        'consultation_participants',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('consultation_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('role', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['consultation_id'], ['consultations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_consultation_participants_consultation_id', 'consultation_participants', ['consultation_id'])

    # Create consultation_evidence table
    op.create_table(
        'consultation_evidence',
        sa.Column('consultation_id', sa.String(), nullable=False),
        sa.Column('evidence_id', sa.String(100), nullable=False),
        sa.Column('linked_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('linked_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['consultation_id'], ['consultations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['linked_by'], ['users.id']),
        sa.PrimaryKeyConstraint('consultation_id', 'evidence_id')
    )


def downgrade() -> None:
    """Drop consultation tables."""
    op.drop_table('consultation_evidence')
    op.drop_index('ix_consultation_participants_consultation_id', table_name='consultation_participants')
    op.drop_table('consultation_participants')
    op.drop_index('ix_consultations_date', table_name='consultations')
    op.drop_index('ix_consultations_case_id', table_name='consultations')
    op.drop_table('consultations')
