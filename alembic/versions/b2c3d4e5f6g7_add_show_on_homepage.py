"""Add show_on_homepage field to blog_posts

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-01-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add show_on_homepage column to blog_posts table."""
    op.add_column('blog_posts', sa.Column('show_on_homepage', sa.Boolean(), nullable=True, server_default='false'))


def downgrade() -> None:
    """Remove show_on_homepage column from blog_posts table."""
    op.drop_column('blog_posts', 'show_on_homepage')
