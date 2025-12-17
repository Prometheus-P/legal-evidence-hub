"""fix_remaining_schema_issues

Revision ID: 4b10g2907f86
Revises: 3a09f1896e75
Create Date: 2025-12-14

Fixes remaining schema mismatches:
1. Add missing columns to messages table (subject, is_read, is_deleted_by_sender, is_deleted_by_recipient)
2. Make messages.case_id nullable
3. Add missing columns to procedure_stage_records table
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b10g2907f86'
down_revision: Union[str, Sequence[str], None] = '3a09f1896e75'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing columns to messages and procedure_stage_records tables."""
    connection = op.get_bind()

    # =========================================
    # 1. Fix messages table
    # =========================================

    # Check existing columns
    result = connection.execute(sa.text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'messages'
    """))
    existing_columns = {row[0] for row in result}

    # Add missing columns
    messages_columns = [
        ('subject', 'VARCHAR(200)', None),
        ('is_read', 'BOOLEAN', 'false'),
        ('is_deleted_by_sender', 'BOOLEAN', 'false'),
        ('is_deleted_by_recipient', 'BOOLEAN', 'false'),
    ]

    for col_name, col_type, default_val in messages_columns:
        if col_name not in existing_columns:
            if default_val:
                op.execute(f'ALTER TABLE messages ADD COLUMN {col_name} {col_type} NOT NULL DEFAULT {default_val}')
            else:
                op.execute(f'ALTER TABLE messages ADD COLUMN {col_name} {col_type}')
            print(f"Added column: messages.{col_name}")

    # Make case_id nullable (Model expects nullable=True)
    op.execute('ALTER TABLE messages ALTER COLUMN case_id DROP NOT NULL')
    print("Made messages.case_id nullable")

    # =========================================
    # 2. Fix procedure_stage_records table
    # =========================================

    result = connection.execute(sa.text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'procedure_stage_records'
    """))
    existing_columns = {row[0] for row in result}

    procedure_columns = [
        ('completed_date', 'TIMESTAMP WITH TIME ZONE', None),
        ('court_reference', 'VARCHAR(100)', None),
        ('judge_name', 'VARCHAR(50)', None),
        ('court_room', 'VARCHAR(50)', None),
        ('outcome', 'VARCHAR(100)', None),
        ('created_by', 'VARCHAR', None),
    ]

    for col_name, col_type, default_val in procedure_columns:
        if col_name not in existing_columns:
            default_clause = f' DEFAULT {default_val}' if default_val else ''
            op.execute(f'ALTER TABLE procedure_stage_records ADD COLUMN {col_name} {col_type}{default_clause}')
            print(f"Added column: procedure_stage_records.{col_name}")


def downgrade() -> None:
    """Remove added columns."""
    # Messages columns
    for col in ['subject', 'is_read', 'is_deleted_by_sender', 'is_deleted_by_recipient']:
        try:
            op.drop_column('messages', col)
        except Exception:
            pass

    # Make case_id NOT NULL again
    try:
        op.execute('ALTER TABLE messages ALTER COLUMN case_id SET NOT NULL')
    except Exception:
        pass

    # Procedure columns
    for col in ['completed_date', 'court_reference', 'judge_name', 'court_room', 'outcome', 'created_by']:
        try:
            op.drop_column('procedure_stage_records', col)
        except Exception:
            pass
