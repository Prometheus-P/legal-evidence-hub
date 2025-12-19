"""Add LSSP v2.10 Keypoint Pipeline tables

Revision ID: lssp_002_keypoint_pipeline
Revises: lssp_001_add_core_tables
Create Date: 2025-12-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'lssp_002_keypoint_pipeline'
down_revision: Union[str, None] = 'lssp_001_add_core_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================
    # v2.10: Keypoint Extraction Rules
    # ============================================
    op.create_table(
        'lssp_keypoint_rules',
        sa.Column('rule_id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('version', sa.String(20), nullable=False, server_default='v2.10'),
        sa.Column('evidence_type', sa.String(40), nullable=False),
        sa.Column('kind', sa.String(40), nullable=False),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('pattern', sa.Text(), nullable=False),
        sa.Column('flags', sa.String(40), nullable=True, server_default=''),
        sa.Column('value_template', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('ground_tags', postgresql.ARRAY(sa.Text()), nullable=True, server_default='{}'),
        sa.Column('base_confidence', sa.Numeric(4, 3), nullable=False, server_default='0.500'),
        sa.Column('base_materiality', sa.Integer(), nullable=False, server_default='40'),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_lssp_kpr_evidence_type', 'lssp_keypoint_rules', ['evidence_type'])
    op.create_index('ix_lssp_kpr_kind', 'lssp_keypoint_rules', ['kind'])

    # ============================================
    # v2.10: Keypoint Extraction Runs (Job Log)
    # ============================================
    op.create_table(
        'lssp_keypoint_extraction_runs',
        sa.Column('run_id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('case_id', sa.String(), nullable=False),
        sa.Column('evidence_id', sa.String(), nullable=False),
        sa.Column('extractor', sa.String(40), nullable=False, server_default='rule_based'),
        sa.Column('version', sa.String(20), nullable=False, server_default='v2.10'),
        sa.Column('status', sa.String(20), nullable=False, server_default='PENDING'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('candidate_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('meta', sa.JSON(), nullable=False, server_default='{}'),
    )
    op.create_index('ix_lssp_ker_case', 'lssp_keypoint_extraction_runs', ['case_id'])
    op.create_index('ix_lssp_ker_evidence', 'lssp_keypoint_extraction_runs', ['evidence_id'])
    op.create_index('ix_lssp_ker_status', 'lssp_keypoint_extraction_runs', ['status'])

    # ============================================
    # v2.10: Keypoint Candidates (Pre-promotion)
    # ============================================
    op.create_table(
        'lssp_keypoint_candidates',
        sa.Column('candidate_id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('case_id', sa.String(), nullable=False),
        sa.Column('evidence_id', sa.String(), nullable=False),
        sa.Column('extract_id', sa.String(), nullable=True),  # Link to evidence_extract
        sa.Column('run_id', sa.BigInteger(), sa.ForeignKey('lssp_keypoint_extraction_runs.run_id'), nullable=True),
        sa.Column('rule_id', sa.BigInteger(), sa.ForeignKey('lssp_keypoint_rules.rule_id'), nullable=True),
        sa.Column('kind', sa.String(40), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),  # Extracted text/statement
        sa.Column('value', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('ground_tags', postgresql.ARRAY(sa.Text()), nullable=True, server_default='{}'),
        sa.Column('confidence', sa.Numeric(4, 3), nullable=False, server_default='0.500'),
        sa.Column('materiality', sa.Integer(), nullable=False, server_default='40'),
        sa.Column('source_span', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('status', sa.String(20), nullable=False, server_default='CANDIDATE'),
        sa.Column('reviewer_id', sa.String(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_lssp_kpc_case', 'lssp_keypoint_candidates', ['case_id'])
    op.create_index('ix_lssp_kpc_evidence', 'lssp_keypoint_candidates', ['evidence_id'])
    op.create_index('ix_lssp_kpc_status', 'lssp_keypoint_candidates', ['status'])
    op.create_index('ix_lssp_kpc_kind', 'lssp_keypoint_candidates', ['kind'])

    # ============================================
    # v2.10: Keypoint Merge Groups
    # ============================================
    op.create_table(
        'lssp_keypoint_merge_groups',
        sa.Column('group_id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('case_id', sa.String(), nullable=False),
        sa.Column('kind', sa.String(40), nullable=False),
        sa.Column('canonical_keypoint_id', sa.String(), nullable=True),  # After promotion
        sa.Column('candidate_ids', postgresql.ARRAY(sa.BigInteger()), nullable=False, server_default='{}'),
        sa.Column('merged_content', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_lssp_kmg_case', 'lssp_keypoint_merge_groups', ['case_id'])

    # ============================================
    # v2.10: Candidate -> Keypoint Link
    # ============================================
    op.create_table(
        'lssp_keypoint_candidate_links',
        sa.Column('candidate_id', sa.BigInteger(), sa.ForeignKey('lssp_keypoint_candidates.candidate_id'), primary_key=True),
        sa.Column('keypoint_id', sa.String(), nullable=False),
        sa.Column('linked_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_lssp_kcl_keypoint', 'lssp_keypoint_candidate_links', ['keypoint_id'])


def downgrade() -> None:
    op.drop_table('lssp_keypoint_candidate_links')
    op.drop_table('lssp_keypoint_merge_groups')
    op.drop_table('lssp_keypoint_candidates')
    op.drop_table('lssp_keypoint_extraction_runs')
    op.drop_table('lssp_keypoint_rules')
