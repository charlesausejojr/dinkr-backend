"""make_hashed_password_nullable

Revision ID: 8161d58c2f96
Revises: ba06adbd2a85
Create Date: 2026-03-02 16:42:01.183320

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8161d58c2f96'
down_revision: Union[str, Sequence[str], None] = 'ba06adbd2a85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('users', 'hashed_password',
               existing_type=sa.VARCHAR(),
               nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('users', 'hashed_password',
               existing_type=sa.VARCHAR(),
               nullable=False)
