"""add_auto_extraction_columns

Revision ID: 012a_auto_extract
Revises: 9fdb562bff2a
Create Date: 2025-12-12 00:00:00.000000

012-precedent-integration: Add auto-extraction tracking columns to party tables
- party_nodes: is_auto_extracted, extraction_confidence, source_evidence_id
- party_relationships: is_auto_extracted, extraction_confidence, evidence_text
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '012a_auto_extract'
down_revision: Union[str, Sequence[str], None] = '9fdb562bff2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add auto-extraction columns to party_nodes and party_relationships tables."""
    # T002: Add columns to party_nodes
    op.add_column('party_nodes',
        sa.Column('is_auto_extracted', sa.Boolean(), nullable=False, server_default='false')
    )
    op.add_column('party_nodes',
        sa.Column('extraction_confidence', sa.Float(), nullable=True)
    )
    op.add_column('party_nodes',
        sa.Column('source_evidence_id', sa.String(length=255), nullable=True)
    )

    # T003: Add columns to party_relationships
    op.add_column('party_relationships',
        sa.Column('is_auto_extracted', sa.Boolean(), nullable=False, server_default='false')
    )
    op.add_column('party_relationships',
        sa.Column('extraction_confidence', sa.Float(), nullable=True)
    )
    op.add_column('party_relationships',
        sa.Column('evidence_text', sa.Text(), nullable=True)
    )

    # T005: Add index on party_nodes(is_auto_extracted)
    op.create_index(
        'idx_party_nodes_auto_extracted',
        'party_nodes',
        ['is_auto_extracted'],
        unique=False
    )

    # T006: Add index on party_relationships(is_auto_extracted)
    op.create_index(
        'idx_party_relationships_auto_extracted',
        'party_relationships',
        ['is_auto_extracted'],
        unique=False
    )


def downgrade() -> None:
    """Remove auto-extraction columns from party tables."""
    # Drop indexes first
    op.drop_index('idx_party_relationships_auto_extracted', table_name='party_relationships')
    op.drop_index('idx_party_nodes_auto_extracted', table_name='party_nodes')

    # Drop columns from party_relationships
    op.drop_column('party_relationships', 'evidence_text')
    op.drop_column('party_relationships', 'extraction_confidence')
    op.drop_column('party_relationships', 'is_auto_extracted')

    # Drop columns from party_nodes
    op.drop_column('party_nodes', 'source_evidence_id')
    op.drop_column('party_nodes', 'extraction_confidence')
    op.drop_column('party_nodes', 'is_auto_extracted')
