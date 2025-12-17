"""Add notification, client_contacts, detective_contacts tables and update messages

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g8
Create Date: 2024-12-12
Issue: #294

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3d4e5f6g7h8'
down_revision = 'b2c3d4e5f6g8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create notification type enum
    notification_type_enum = sa.Enum(
        'case_update', 'message', 'evidence', 'deadline', 'system',
        name='notificationtype'
    )
    notification_type_enum.create(op.get_bind(), checkfirst=True)

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('type', notification_type_enum, nullable=False, server_default='system'),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('content', sa.String(500), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('related_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Create client_contacts table
    op.create_table(
        'client_contacts',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('lawyer_id', sa.String(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('memo', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create detective_contacts table
    op.create_table(
        'detective_contacts',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('lawyer_id', sa.String(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('specialty', sa.String(100), nullable=True),
        sa.Column('memo', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Update messages table - add new columns
    op.add_column('messages', sa.Column('subject', sa.String(200), nullable=True))
    op.add_column('messages', sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('messages', sa.Column('is_deleted_by_sender', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('messages', sa.Column('is_deleted_by_recipient', sa.Boolean(), nullable=False, server_default='false'))

    # Make case_id nullable in messages
    op.alter_column('messages', 'case_id', existing_type=sa.String(), nullable=True)


def downgrade() -> None:
    # Revert messages table changes
    op.alter_column('messages', 'case_id', existing_type=sa.String(), nullable=False)
    op.drop_column('messages', 'is_deleted_by_recipient')
    op.drop_column('messages', 'is_deleted_by_sender')
    op.drop_column('messages', 'is_read')
    op.drop_column('messages', 'subject')

    # Drop new tables
    op.drop_table('detective_contacts')
    op.drop_table('client_contacts')
    op.drop_table('notifications')

    # Drop enum
    sa.Enum(name='notificationtype').drop(op.get_bind(), checkfirst=True)
