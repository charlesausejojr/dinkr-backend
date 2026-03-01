"""add_schedule_to_coaches

Revision ID: c5883226678e
Revises: 3cc3b386ccf0
Create Date: 2026-03-02 01:57:24.131578

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c5883226678e'
down_revision: Union[str, Sequence[str], None] = '3cc3b386ccf0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_DEFAULT_SCHEDULE = {
    day: {"open": "06:00", "close": "22:00", "closed": False}
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
}


def upgrade() -> None:
    import json
    op.add_column('coaches', sa.Column(
        'schedule',
        postgresql.JSONB(astext_type=sa.Text()),
        nullable=False,
        server_default=json.dumps(_DEFAULT_SCHEDULE),
    ))


def downgrade() -> None:
    op.drop_column('coaches', 'schedule')
