"""Add asset division tables

Revision ID: d8e9f0a1b2c3
Revises: c7e5f1a2b3c4
Create Date: 2024-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8e9f0a1b2c3'
down_revision: Union[str, None] = 'c7e5f1a2b3c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create assets table
    op.create_table(
        'assets',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('case_id', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),  # AssetCategory enum
        sa.Column('ownership', sa.String(), nullable=False),  # AssetOwnership enum
        sa.Column('nature', sa.String(), nullable=False, server_default='marital'),  # AssetNature enum
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('acquisition_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('acquisition_value', sa.Integer(), nullable=True),
        sa.Column('current_value', sa.Integer(), nullable=False),
        sa.Column('valuation_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('valuation_source', sa.String(200), nullable=True),
        sa.Column('division_ratio_plaintiff', sa.Integer(), nullable=True, server_default='50'),
        sa.Column('division_ratio_defendant', sa.Integer(), nullable=True, server_default='50'),
        sa.Column('proposed_allocation', sa.String(), nullable=True),  # AssetOwnership enum
        sa.Column('evidence_id', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
    )
    op.create_index('ix_assets_case_id', 'assets', ['case_id'])

    # Create asset_division_summaries table
    op.create_table(
        'asset_division_summaries',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('case_id', sa.String(), nullable=False),
        sa.Column('total_marital_assets', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_separate_plaintiff', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_separate_defendant', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_debts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('net_marital_value', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('plaintiff_share', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('defendant_share', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('settlement_amount', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('plaintiff_ratio', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('defendant_ratio', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('plaintiff_holdings', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('defendant_holdings', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('calculated_by', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['calculated_by'], ['users.id']),
    )
    op.create_index('ix_asset_division_summaries_case_id', 'asset_division_summaries', ['case_id'])


def downgrade() -> None:
    op.drop_index('ix_asset_division_summaries_case_id')
    op.drop_table('asset_division_summaries')
    op.drop_index('ix_assets_case_id')
    op.drop_table('assets')
