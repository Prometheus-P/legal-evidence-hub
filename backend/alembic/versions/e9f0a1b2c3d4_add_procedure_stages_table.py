"""Add procedure stages table

Revision ID: e9f0a1b2c3d4
Revises: d8e9f0a1b2c3
Create Date: 2024-01-16 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9f0a1b2c3d4'
down_revision: Union[str, None] = 'd8e9f0a1b2c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create procedure_stage_records table
    op.create_table(
        'procedure_stage_records',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('case_id', sa.String(), nullable=False),

        # Stage info
        sa.Column('stage', sa.String(), nullable=False),  # ProcedureStageType enum
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),  # StageStatus enum
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),

        # Dates
        sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_date', sa.DateTime(timezone=True), nullable=True),

        # Court info
        sa.Column('court_reference', sa.String(100), nullable=True),
        sa.Column('judge_name', sa.String(50), nullable=True),
        sa.Column('court_room', sa.String(50), nullable=True),

        # Details
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('documents', sa.JSON(), nullable=True),
        sa.Column('outcome', sa.String(100), nullable=True),

        # Metadata
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_procedure_stage_records_case_id', 'procedure_stage_records', ['case_id'])
    op.create_index('ix_procedure_stage_records_stage', 'procedure_stage_records', ['stage'])
    op.create_index('ix_procedure_stage_records_status', 'procedure_stage_records', ['status'])


def downgrade() -> None:
    op.drop_index('ix_procedure_stage_records_status', 'procedure_stage_records')
    op.drop_index('ix_procedure_stage_records_stage', 'procedure_stage_records')
    op.drop_index('ix_procedure_stage_records_case_id', 'procedure_stage_records')
    op.drop_table('procedure_stage_records')
