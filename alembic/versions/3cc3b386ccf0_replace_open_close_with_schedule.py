"""replace_open_close_with_schedule

Revision ID: 3cc3b386ccf0
Revises: 39cfe0c9dfa4
Create Date: 2026-03-02 01:23:35.519328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3cc3b386ccf0'
down_revision: Union[str, Sequence[str], None] = '39cfe0c9dfa4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_DEFAULT_SCHEDULE = {
    day: {"open": "06:00", "close": "22:00", "closed": False}
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
}


def upgrade() -> None:
    """Upgrade schema."""
    import json
    op.add_column('establishments', sa.Column(
        'schedule',
        postgresql.JSONB(astext_type=sa.Text()),
        nullable=False,
        server_default=json.dumps(_DEFAULT_SCHEDULE),
    ))
    op.drop_column('establishments', 'open_time')
    op.drop_column('establishments', 'close_time')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('establishments', sa.Column('close_time', sa.VARCHAR(), server_default=sa.text("'22:00'::character varying"), nullable=False))
    op.add_column('establishments', sa.Column('open_time', sa.VARCHAR(), server_default=sa.text("'06:00'::character varying"), nullable=False))
    op.drop_column('establishments', 'schedule')
