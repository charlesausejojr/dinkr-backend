"""add_image_url_to_courts

Revision ID: afb6f9373eed
Revises: 06b58c0ef260
Create Date: 2026-02-27 21:22:13.692221

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afb6f9373eed'
down_revision: Union[str, Sequence[str], None] = '06b58c0ef260'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('courts', sa.Column('image_url', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('courts', 'image_url')
