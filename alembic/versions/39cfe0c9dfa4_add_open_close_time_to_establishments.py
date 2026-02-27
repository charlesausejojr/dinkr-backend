"""add_open_close_time_to_establishments

Revision ID: 39cfe0c9dfa4
Revises: afb6f9373eed
Create Date: 2026-02-27 22:06:58.156719

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39cfe0c9dfa4'
down_revision: Union[str, Sequence[str], None] = 'afb6f9373eed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('establishments', sa.Column('open_time', sa.String(), server_default='06:00', nullable=False))
    op.add_column('establishments', sa.Column('close_time', sa.String(), server_default='22:00', nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('establishments', 'close_time')
    op.drop_column('establishments', 'open_time')
