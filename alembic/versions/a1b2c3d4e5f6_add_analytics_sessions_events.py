"""Add analytics sessions and events tables

Revision ID: a1b2c3d4e5f6
Revises: 75056f0eeff5
Create Date: 2026-01-28 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '75056f0eeff5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create analytics_sessions table
    op.create_table('analytics_sessions',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('ip_hash', sa.String(length=64), nullable=False),
        sa.Column('pages_visited', sa.Integer(), nullable=True),
        sa.Column('consent_given', sa.Boolean(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analytics_sessions_started_at'), 'analytics_sessions', ['started_at'], unique=False)
    op.create_index(op.f('ix_analytics_sessions_ip_hash'), 'analytics_sessions', ['ip_hash'], unique=False)

    # Create analytics_events table
    op.create_table('analytics_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('event_data', sa.Text(), nullable=True),
        sa.Column('path', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['analytics_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analytics_events_timestamp'), 'analytics_events', ['timestamp'], unique=False)
    op.create_index(op.f('ix_analytics_events_session_id'), 'analytics_events', ['session_id'], unique=False)
    op.create_index(op.f('ix_analytics_events_event_type'), 'analytics_events', ['event_type'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_analytics_events_event_type'), table_name='analytics_events')
    op.drop_index(op.f('ix_analytics_events_session_id'), table_name='analytics_events')
    op.drop_index(op.f('ix_analytics_events_timestamp'), table_name='analytics_events')
    op.drop_table('analytics_events')
    op.drop_index(op.f('ix_analytics_sessions_ip_hash'), table_name='analytics_sessions')
    op.drop_index(op.f('ix_analytics_sessions_started_at'), table_name='analytics_sessions')
    op.drop_table('analytics_sessions')
