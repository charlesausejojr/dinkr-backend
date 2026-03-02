"""add_lat_lng_to_establishments

Revision ID: ba06adbd2a85
Revises: c5883226678e
Create Date: 2026-03-02 16:14:07.029445

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba06adbd2a85'
down_revision: Union[str, Sequence[str], None] = 'c5883226678e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('establishments', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('establishments', sa.Column('longitude', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('establishments', 'longitude')
    op.drop_column('establishments', 'latitude')
