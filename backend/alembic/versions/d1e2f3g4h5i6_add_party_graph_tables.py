"""add_party_graph_tables

Revision ID: d1e2f3g4h5i6
Revises: 8cbbd417e515
Create Date: 2025-12-08 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1e2f3g4h5i6'
down_revision: Union[str, Sequence[str], None] = '8cbbd417e515'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create party_nodes, party_relationships, and evidence_party_links tables."""
    # Create party_nodes table first (no FK dependencies on other new tables)
    op.create_table('party_nodes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('case_id', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('PLAINTIFF', 'DEFENDANT', 'THIRD_PARTY', 'CHILD', 'FAMILY', name='partytype'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('alias', sa.String(length=50), nullable=True),
        sa.Column('birth_year', sa.Integer(), nullable=True),
        sa.Column('occupation', sa.String(length=100), nullable=True),
        sa.Column('position_x', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('position_y', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_party_nodes_case_id'), 'party_nodes', ['case_id'], unique=False)

    # Create party_relationships table (depends on party_nodes)
    op.create_table('party_relationships',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('case_id', sa.String(), nullable=False),
        sa.Column('source_party_id', sa.String(), nullable=False),
        sa.Column('target_party_id', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('MARRIAGE', 'AFFAIR', 'PARENT_CHILD', 'SIBLING', 'IN_LAW', 'COHABIT', name='relationshiptype'), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_party_id'], ['party_nodes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_party_id'], ['party_nodes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_party_relationships_case_id'), 'party_relationships', ['case_id'], unique=False)
    op.create_index(op.f('ix_party_relationships_source_party_id'), 'party_relationships', ['source_party_id'], unique=False)
    op.create_index(op.f('ix_party_relationships_target_party_id'), 'party_relationships', ['target_party_id'], unique=False)

    # Create evidence_party_links table (depends on party_nodes and party_relationships)
    op.create_table('evidence_party_links',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('case_id', sa.String(), nullable=False),
        sa.Column('evidence_id', sa.String(length=100), nullable=False),
        sa.Column('party_id', sa.String(), nullable=True),
        sa.Column('relationship_id', sa.String(), nullable=True),
        sa.Column('link_type', sa.Enum('MENTIONS', 'PROVES', 'INVOLVES', 'CONTRADICTS', name='linktype'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['party_id'], ['party_nodes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['relationship_id'], ['party_relationships.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_evidence_party_links_case_id'), 'evidence_party_links', ['case_id'], unique=False)
    op.create_index(op.f('ix_evidence_party_links_evidence_id'), 'evidence_party_links', ['evidence_id'], unique=False)
    op.create_index(op.f('ix_evidence_party_links_party_id'), 'evidence_party_links', ['party_id'], unique=False)
    op.create_index(op.f('ix_evidence_party_links_relationship_id'), 'evidence_party_links', ['relationship_id'], unique=False)


def downgrade() -> None:
    """Drop party graph tables in reverse order."""
    # Drop evidence_party_links first (depends on others)
    op.drop_index(op.f('ix_evidence_party_links_relationship_id'), table_name='evidence_party_links')
    op.drop_index(op.f('ix_evidence_party_links_party_id'), table_name='evidence_party_links')
    op.drop_index(op.f('ix_evidence_party_links_evidence_id'), table_name='evidence_party_links')
    op.drop_index(op.f('ix_evidence_party_links_case_id'), table_name='evidence_party_links')
    op.drop_table('evidence_party_links')

    # Drop party_relationships (depends on party_nodes)
    op.drop_index(op.f('ix_party_relationships_target_party_id'), table_name='party_relationships')
    op.drop_index(op.f('ix_party_relationships_source_party_id'), table_name='party_relationships')
    op.drop_index(op.f('ix_party_relationships_case_id'), table_name='party_relationships')
    op.drop_table('party_relationships')

    # Drop party_nodes last
    op.drop_index(op.f('ix_party_nodes_case_id'), table_name='party_nodes')
    op.drop_table('party_nodes')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS linktype')
    op.execute('DROP TYPE IF EXISTS relationshiptype')
    op.execute('DROP TYPE IF EXISTS partytype')
