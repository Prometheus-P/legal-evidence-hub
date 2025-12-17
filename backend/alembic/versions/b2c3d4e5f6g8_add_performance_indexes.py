"""add_performance_indexes

Revision ID: b2c3d4e5f6g8
Revises: a1b2c3d4e5f7
Create Date: 2025-12-12

Issue #277: Add missing database indexes for frequently queried columns.
Improves query performance from O(n) to O(log n) by eliminating full table scans.

Indexes added:
- case_members: user_id, (case_id, user_id) composite
- audit_logs: user_id, timestamp
- calendar_events: start_time, (user_id, case_id) composite
- investigation_records: detective_id, (case_id, detective_id) composite
- detective_earnings: (detective_id, created_at) composite
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g8'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes for frequently queried columns."""

    # Case Members - used in _get_accessible_case_ids() and verify_case_*_access()
    # Note: case_members has composite PK (case_id, user_id), but user_id alone needs index
    op.create_index(
        'ix_case_members_user_id',
        'case_members',
        ['user_id']
    )

    # Audit Logs - used in audit_log_repository queries
    op.create_index(
        'ix_audit_logs_user_id',
        'audit_logs',
        ['user_id']
    )
    op.create_index(
        'ix_audit_logs_timestamp',
        'audit_logs',
        ['timestamp']
    )

    # Calendar Events - used in dashboard_service date range queries
    op.create_index(
        'ix_calendar_events_start_time',
        'calendar_events',
        ['start_time']
    )
    op.create_index(
        'ix_calendar_events_user_case',
        'calendar_events',
        ['user_id', 'case_id']
    )

    # Investigation Records - used in detective_portal_service
    op.create_index(
        'ix_investigation_records_detective_id',
        'investigation_records',
        ['detective_id']
    )
    op.create_index(
        'ix_investigation_records_case_detective',
        'investigation_records',
        ['case_id', 'detective_id']
    )

    # Detective Earnings - used in earnings aggregation queries
    # Note: individual indexes already exist, add composite for time-range queries
    op.create_index(
        'ix_detective_earnings_detective_time',
        'detective_earnings',
        ['detective_id', 'created_at']
    )


def downgrade() -> None:
    """Drop all performance indexes."""

    # Detective Earnings
    op.drop_index('ix_detective_earnings_detective_time', 'detective_earnings')

    # Investigation Records
    op.drop_index('ix_investigation_records_case_detective', 'investigation_records')
    op.drop_index('ix_investigation_records_detective_id', 'investigation_records')

    # Calendar Events
    op.drop_index('ix_calendar_events_user_case', 'calendar_events')
    op.drop_index('ix_calendar_events_start_time', 'calendar_events')

    # Audit Logs
    op.drop_index('ix_audit_logs_timestamp', 'audit_logs')
    op.drop_index('ix_audit_logs_user_id', 'audit_logs')

    # Case Members
    op.drop_index('ix_case_members_user_id', 'case_members')
