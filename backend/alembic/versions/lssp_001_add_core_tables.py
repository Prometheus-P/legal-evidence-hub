"""Add LSSP tables v2.01-v2.04

Revision ID: lssp_001_add_core_tables
Revises: f2a3b4c5d6e7
Create Date: 2025-12-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'lssp_001_add_core_tables'
down_revision: Union[str, None] = 'f2a3b4c5d6e7'  # Point to latest migration
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================
    # v2.01: Legal Grounds (Seed)
    # ============================================
    op.create_table(
        'lssp_legal_grounds',
        sa.Column('code', sa.String(10), primary_key=True),
        sa.Column('name_ko', sa.String(100), nullable=False),
        sa.Column('elements', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('limitation', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('version', sa.String(20), nullable=False, server_default='v2.01'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'lssp_case_legal_ground_links',
        sa.Column('case_id', sa.String(), nullable=False),
        sa.Column('ground_code', sa.String(10), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('strength_score', sa.String(20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('assessed_by', sa.String(), nullable=True),
        sa.Column('assessed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('case_id', 'ground_code'),
    )
    op.create_index('ix_lssp_clgl_case', 'lssp_case_legal_ground_links', ['case_id'])

    # ============================================
    # v2.03: Evidence Extracts & Keypoints
    # ============================================
    op.create_table(
        'lssp_evidence_extracts',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('case_id', sa.String(), sa.ForeignKey('cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('evidence_file_id', sa.String(), sa.ForeignKey('evidence.id', ondelete='CASCADE'), nullable=False),
        sa.Column('kind', sa.String(30), nullable=False),
        sa.Column('locator', sa.JSON(), nullable=False),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_lssp_extracts_case', 'lssp_evidence_extracts', ['case_id'])
    op.create_index('ix_lssp_extracts_file', 'lssp_evidence_extracts', ['evidence_file_id'])

    op.create_table(
        'lssp_keypoints',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('case_id', sa.String(), sa.ForeignKey('cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('statement', sa.Text(), nullable=False),
        sa.Column('occurred_at', sa.Date(), nullable=True),
        sa.Column('occurred_at_precision', sa.String(20), nullable=False, server_default='DATE'),
        sa.Column('actors', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('amount', sa.Numeric(18, 2), nullable=True),
        sa.Column('currency', sa.String(10), nullable=True, server_default='KRW'),
        sa.Column('type_code', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='DRAFT'),
        sa.Column('risk_flags', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_lssp_keypoints_case', 'lssp_keypoints', ['case_id'])
    op.create_index('ix_lssp_keypoints_status', 'lssp_keypoints', ['status'])
    op.create_index('ix_lssp_keypoints_type', 'lssp_keypoints', ['type_code'])

    op.create_table(
        'lssp_keypoint_extract_links',
        sa.Column('keypoint_id', sa.String(), sa.ForeignKey('lssp_keypoints.id', ondelete='CASCADE'), nullable=False),
        sa.Column('extract_id', sa.String(), sa.ForeignKey('lssp_evidence_extracts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('keypoint_id', 'extract_id'),
    )

    op.create_table(
        'lssp_keypoint_ground_links',
        sa.Column('keypoint_id', sa.String(), sa.ForeignKey('lssp_keypoints.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ground_code', sa.String(10), nullable=False),
        sa.Column('element_tag', sa.String(100), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('keypoint_id', 'ground_code', 'element_tag'),
    )
    op.create_index('ix_lssp_kgl_ground', 'lssp_keypoint_ground_links', ['ground_code'])

    # ============================================
    # v2.04: Draft Templates & Blocks (Seed)
    # ============================================
    op.create_table(
        'lssp_draft_templates',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('label', sa.String(100), nullable=False),
        sa.Column('schema', sa.JSON(), nullable=False),
        sa.Column('version', sa.String(20), nullable=False, server_default='v2.04'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'lssp_draft_blocks',
        sa.Column('id', sa.String(100), primary_key=True),
        sa.Column('label', sa.String(200), nullable=False),
        sa.Column('block_tag', sa.String(50), nullable=False),
        sa.Column('template', sa.Text(), nullable=False),
        sa.Column('required_keypoint_types', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('required_evidence_tags', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('conditions', sa.String(500), nullable=True),
        sa.Column('legal_refs', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('version', sa.String(20), nullable=False, server_default='v2.04'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_lssp_draft_blocks_tag', 'lssp_draft_blocks', ['block_tag'])

    # ============================================
    # v2.04: Draft Instances
    # ============================================
    op.create_table(
        'lssp_drafts',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('case_id', sa.String(), sa.ForeignKey('cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('template_id', sa.String(50), sa.ForeignKey('lssp_draft_templates.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('meta', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('coverage_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(20), nullable=False, server_default='DRAFTING'),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_lssp_drafts_case', 'lssp_drafts', ['case_id'])
    op.create_index('ix_lssp_drafts_status', 'lssp_drafts', ['status'])

    op.create_table(
        'lssp_draft_block_instances',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('draft_id', sa.String(), sa.ForeignKey('lssp_drafts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('block_id', sa.String(100), sa.ForeignKey('lssp_draft_blocks.id'), nullable=False),
        sa.Column('section_key', sa.String(50), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='AUTO'),
        sa.Column('coverage_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_lssp_dbi_draft', 'lssp_draft_block_instances', ['draft_id'])

    op.create_table(
        'lssp_draft_citations',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('block_instance_id', sa.String(), sa.ForeignKey('lssp_draft_block_instances.id', ondelete='CASCADE'), nullable=False),
        sa.Column('keypoint_id', sa.String(), sa.ForeignKey('lssp_keypoints.id', ondelete='SET NULL'), nullable=True),
        sa.Column('extract_id', sa.String(), sa.ForeignKey('lssp_evidence_extracts.id', ondelete='SET NULL'), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint('(keypoint_id IS NOT NULL) OR (extract_id IS NOT NULL)', name='ck_citation_one_ref'),
    )
    op.create_index('ix_lssp_citations_block', 'lssp_draft_citations', ['block_instance_id'])

    op.create_table(
        'lssp_draft_precedent_links',
        sa.Column('draft_id', sa.String(), sa.ForeignKey('lssp_drafts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('precedent_id', sa.String(100), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('draft_id', 'precedent_id'),
    )


def downgrade() -> None:
    # Drop in reverse order
    op.drop_table('lssp_draft_precedent_links')
    op.drop_index('ix_lssp_citations_block')
    op.drop_table('lssp_draft_citations')
    op.drop_index('ix_lssp_dbi_draft')
    op.drop_table('lssp_draft_block_instances')
    op.drop_index('ix_lssp_drafts_status')
    op.drop_index('ix_lssp_drafts_case')
    op.drop_table('lssp_drafts')
    op.drop_index('ix_lssp_draft_blocks_tag')
    op.drop_table('lssp_draft_blocks')
    op.drop_table('lssp_draft_templates')
    op.drop_index('ix_lssp_kgl_ground')
    op.drop_table('lssp_keypoint_ground_links')
    op.drop_table('lssp_keypoint_extract_links')
    op.drop_index('ix_lssp_keypoints_type')
    op.drop_index('ix_lssp_keypoints_status')
    op.drop_index('ix_lssp_keypoints_case')
    op.drop_table('lssp_keypoints')
    op.drop_index('ix_lssp_extracts_file')
    op.drop_index('ix_lssp_extracts_case')
    op.drop_table('lssp_evidence_extracts')
    op.drop_index('ix_lssp_clgl_case')
    op.drop_table('lssp_case_legal_ground_links')
    op.drop_table('lssp_legal_grounds')
