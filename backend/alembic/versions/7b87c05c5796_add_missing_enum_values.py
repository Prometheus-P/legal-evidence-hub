"""add_missing_enum_values

Revision ID: 7b87c05c5796
Revises: 0e18fdc9e742
Create Date: 2025-12-09

Add missing enum values to PostgreSQL enum types.
PostgreSQL enums are strict - values must be explicitly added.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b87c05c5796'
down_revision: Union[str, Sequence[str], None] = '0e18fdc9e742'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Enum values that need to be added (enum_name, values_to_add)
ENUM_VALUES_TO_ADD = [
    # CaseStatus - add all values
    ('casestatus', ['active', 'open', 'in_progress', 'closed']),
    # UserRole - add all values
    ('userrole', ['lawyer', 'staff', 'admin', 'client', 'detective']),
    # UserStatus - add all values
    ('userstatus', ['active', 'inactive', 'suspended', 'pending']),
    # CaseMemberRole - add all values
    ('casememberrole', ['owner', 'member', 'viewer']),
    # EvidenceStatus - add all values
    ('evidencestatus', ['pending', 'processing', 'completed', 'failed']),
    # EvidenceType - add all values
    ('evidencetype', ['image', 'audio', 'video', 'text', 'pdf', 'document', 'other']),
    # DraftStatus - add all values
    ('draftstatus', ['draft', 'pending_review', 'approved', 'rejected', 'final']),
    # InvoiceStatus - add all values
    ('invoicestatus', ['pending', 'paid', 'overdue', 'cancelled']),
    # PaymentStatus - add all values
    ('paymentstatus', ['pending', 'completed', 'failed', 'refunded']),
    # AssetType - add all values
    ('assettype', ['real_estate', 'vehicle', 'financial', 'business', 'personal', 'other', 'debt']),
    # OwnershipType - add all values
    ('ownershiptype', ['plaintiff', 'defendant', 'joint']),
    # ProcedureStageType - add all values
    ('procedurestagetype', ['consultation', 'filing', 'mediation', 'trial', 'judgment', 'appeal', 'settlement', 'enforcement']),
    # StageStatus - add all values
    ('stagestatus', ['pending', 'in_progress', 'completed', 'skipped']),
]


def upgrade() -> None:
    """Add missing enum values to PostgreSQL enums."""
    connection = op.get_bind()

    for enum_name, values in ENUM_VALUES_TO_ADD:
        # Check if enum type exists
        result = connection.execute(sa.text(
            f"SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{enum_name}')"
        ))
        if not result.scalar():
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
                except Exception as e:
                    print(f"Warning: Could not add '{value}' to {enum_name}: {e}")


def downgrade() -> None:
    """Cannot remove enum values in PostgreSQL without recreating the type."""
    pass
