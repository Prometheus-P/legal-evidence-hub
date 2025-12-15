"""fix_schema_model_mismatch

Revision ID: 3a09f1896e75
Revises: 2a08f0895d64
Create Date: 2025-12-14

Fixes schema mismatches between models.py and actual database:
1. Add missing columns to asset_division_summaries table
2. Add missing lowercase enum values for StrEnumColumn compatibility
3. Add missing enum values (casestatus.review, assetnature.separate)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a09f1896e75'
down_revision: Union[str, Sequence[str], None] = '2a08f0895d64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Enums that need lowercase values added
ENUMS_NEEDING_LOWERCASE = [
    ('assetcategory', ['real_estate', 'savings', 'stocks', 'retirement', 'vehicle', 'insurance', 'debt', 'other']),
    ('assetnature', ['premarital', 'marital', 'mixed', 'separate']),  # separate is new
    ('assetownership', ['plaintiff', 'defendant', 'joint']),
    ('confidencelevel', ['high', 'medium', 'low']),
    ('documenttype', ['complaint', 'motion', 'brief', 'response']),
    ('exportformat', ['docx', 'pdf']),
    ('exportjobstatus', ['pending', 'processing', 'completed', 'failed']),
    ('investigationrecordtype', ['location', 'photo', 'video', 'audio', 'memo', 'evidence']),
    ('jobstatus', ['queued', 'processing', 'completed', 'failed', 'retry', 'cancelled']),
    ('jobtype', ['ocr', 'stt', 'vision', 'draft', 'analysis', 'pdf_export', 'docx_export']),
    ('linktype', ['mentions', 'proves', 'involves', 'contradicts']),
    ('notificationfrequency', ['immediate', 'daily', 'weekly']),
    ('partytype', ['plaintiff', 'defendant', 'third_party', 'child', 'family']),
    ('procedurestagetype', ['filed', 'served', 'answered', 'mediation', 'mediation_closed', 'trial', 'judgment', 'appeal', 'final']),
    ('profilevisibility', ['public', 'team', 'private']),
    ('propertyowner', ['plaintiff', 'defendant', 'joint']),
    ('propertytype', ['real_estate', 'savings', 'stocks', 'retirement', 'vehicle', 'insurance', 'debt', 'other']),
    ('relationshiptype', ['marriage', 'affair', 'parent_child', 'sibling', 'in_law', 'cohabit']),
    ('stagestatus', ['pending', 'in_progress', 'completed', 'skipped']),
    # Also add missing values to existing enums
    ('casestatus', ['review']),  # Missing 'review' value
    ('evidencestatus', ['uploaded']),  # Missing 'uploaded' value
]


def upgrade() -> None:
    """
    1. Add missing columns to asset_division_summaries
    2. Add lowercase enum values for StrEnumColumn compatibility
    """
    connection = op.get_bind()

    # =========================================
    # 1. Add missing columns to asset_division_summaries
    # =========================================

    # Check existing columns first
    result = connection.execute(sa.text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'asset_division_summaries'
    """))
    existing_columns = {row[0] for row in result}

    columns_to_add = [
        ('total_marital_assets', 'INTEGER', '0'),
        ('total_separate_plaintiff', 'INTEGER', '0'),
        ('total_separate_defendant', 'INTEGER', '0'),
        ('net_marital_value', 'INTEGER', '0'),
        ('plaintiff_share', 'INTEGER', '0'),
        ('defendant_share', 'INTEGER', '0'),
        ('settlement_amount', 'INTEGER', '0'),
        ('plaintiff_ratio', 'INTEGER', '50'),
        ('defendant_ratio', 'INTEGER', '50'),
        ('plaintiff_holdings', 'INTEGER', '0'),
        ('defendant_holdings', 'INTEGER', '0'),
        ('notes', 'TEXT', None),
        ('calculated_at', 'TIMESTAMP WITH TIME ZONE', None),
        ('calculated_by', 'VARCHAR', None),
    ]

    for col_name, col_type, default_val in columns_to_add:
        if col_name not in existing_columns:
            default_clause = f" DEFAULT {default_val}" if default_val else ""
            op.execute(f'ALTER TABLE asset_division_summaries ADD COLUMN {col_name} {col_type}{default_clause}')
            print(f"Added column: asset_division_summaries.{col_name}")

    # =========================================
    # 2. Add lowercase enum values
    # =========================================

    for enum_name, values in ENUMS_NEEDING_LOWERCASE:
        # Check if enum type exists
        result = connection.execute(sa.text(
            f"SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{enum_name}')"
        ))
        if not result.scalar():
            print(f"Enum {enum_name} does not exist, skipping")
            continue

        # Get existing enum values
        result = connection.execute(sa.text(
            f"SELECT unnest(enum_range(NULL::{enum_name}))::text"
        ))
        existing_values = {row[0] for row in result}

        # Add missing values
        for value in values:
            if value not in existing_values:
                try:
                    op.execute(f"ALTER TYPE {enum_name} ADD VALUE IF NOT EXISTS '{value}'")
                    print(f"Added enum value: {enum_name}.{value}")
                except Exception as e:
                    print(f"Warning: Could not add '{value}' to {enum_name}: {e}")


def downgrade() -> None:
    """
    Cannot easily remove enum values or columns in PostgreSQL.
    This migration is effectively one-way for safety.
    """
    # Drop added columns from asset_division_summaries if needed
    columns_to_drop = [
        'total_marital_assets', 'total_separate_plaintiff', 'total_separate_defendant',
        'net_marital_value', 'plaintiff_share', 'defendant_share', 'settlement_amount',
        'plaintiff_ratio', 'defendant_ratio', 'plaintiff_holdings', 'defendant_holdings',
        'notes', 'calculated_at', 'calculated_by'
    ]

    for col_name in columns_to_drop:
        try:
            op.drop_column('asset_division_summaries', col_name)
        except Exception:
            pass  # Column might not exist
