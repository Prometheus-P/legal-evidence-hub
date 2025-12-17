"""add case checklist status table

Revision ID: c7e5f1a2b3c4
Revises: 699278a17740
Create Date: 2025-02-22 11:20:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c7e5f1a2b3c4'
down_revision = '699278a17740'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'case_checklist_statuses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('case_id', sa.String(), nullable=False),
        sa.Column('item_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('case_id', 'item_id', name='uq_case_checklist_item'),
    )
    op.create_index('ix_case_checklist_statuses_case_id', 'case_checklist_statuses', ['case_id'], unique=False)
    op.create_index('ix_case_checklist_statuses_updated_by', 'case_checklist_statuses', ['updated_by'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_case_checklist_statuses_updated_by', table_name='case_checklist_statuses')
    op.drop_index('ix_case_checklist_statuses_case_id', table_name='case_checklist_statuses')
    op.drop_table('case_checklist_statuses')
