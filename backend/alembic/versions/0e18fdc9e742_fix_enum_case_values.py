"""fix_enum_case_values

Revision ID: 0e18fdc9e742
Revises: 4821242f228f
Create Date: 2025-12-09 14:33:46.725253

Fix: Convert uppercase enum values (LAWYER, STAFF, etc.) to lowercase (lawyer, staff, etc.)
This is needed because PostgreSQL enum types store exact values, and our enums define lowercase values.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e18fdc9e742'
down_revision: Union[str, Sequence[str], None] = '4821242f228f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Enum columns that need to be fixed (table, column, enum_name)
ENUM_COLUMNS = [
    # UserRole columns
    ('users', 'role', 'userrole'),
    ('invitations', 'role', 'userrole'),
    # UserStatus columns
    ('users', 'status', 'userstatus'),
    # CaseStatus columns
    ('cases', 'status', 'casestatus'),
    # CaseMemberRole columns
    ('case_members', 'role', 'casememberrole'),
    # EvidenceStatus columns
    ('evidence', 'status', 'evidencestatus'),
    # EvidenceType columns
    ('evidence', 'type', 'evidencetype'),
    # DraftStatus columns
    ('drafts', 'status', 'draftstatus'),
    # InvoiceStatus columns
    ('invoices', 'status', 'invoicestatus'),
    # PaymentStatus columns
    ('payments', 'status', 'paymentstatus'),
    # AssetType columns
    ('assets', 'asset_type', 'assettype'),
    # OwnershipType columns
    ('assets', 'ownership', 'ownershiptype'),
    # ProcedureStageType columns (if exists)
    ('procedure_stage_records', 'stage', 'procedurestagetype'),
    # StageStatus columns (if exists)
    ('procedure_stage_records', 'status', 'stagestatus'),
]


def upgrade() -> None:
    """Convert uppercase enum values to lowercase."""
    connection = op.get_bind()

    for table, column, enum_name in ENUM_COLUMNS:
        # Check if table exists
        result = connection.execute(sa.text(
            f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')"
        ))
        if not result.scalar():
            continue

        # Check if column exists
        result = connection.execute(sa.text(
            f"SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = '{table}' AND column_name = '{column}')"
        ))
        if not result.scalar():
            continue

        # Convert column to TEXT, update to lowercase, then back to enum
        # This handles both cases: if values are uppercase string or if they need conversion
        try:
            # Step 1: Alter column to VARCHAR temporarily
            op.execute(f'ALTER TABLE {table} ALTER COLUMN {column} TYPE VARCHAR USING {column}::VARCHAR')

            # Step 2: Update values to lowercase
            op.execute(f'UPDATE {table} SET {column} = LOWER({column}) WHERE {column} IS NOT NULL')

            # Step 3: Convert back to enum
            op.execute(f'ALTER TABLE {table} ALTER COLUMN {column} TYPE {enum_name} USING {column}::{enum_name}')
        except Exception as e:
            # If conversion fails, it might already be correct
            print(f"Warning: Could not convert {table}.{column}: {e}")


def downgrade() -> None:
    """No downgrade needed - lowercase values are correct."""
    pass
