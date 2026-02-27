"""add_booking_indexes

Revision ID: 06b58c0ef260
Revises: 39e163f29c2f
Create Date: 2026-02-27 18:37:04.472473

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '06b58c0ef260'
down_revision: Union[str, Sequence[str], None] = '39e163f29c2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('ix_courts_establishment_id', 'courts', ['establishment_id'])
    op.create_index('ix_bookings_court_date', 'bookings', ['court_id', 'date'])
    op.create_index('ix_bookings_coach_date', 'bookings', ['coach_id', 'date'])
    op.create_index('ix_coach_bookings_coach_date', 'coach_bookings', ['coach_id', 'date'])
    op.create_index('ix_establishments_is_active', 'establishments', ['is_active'])
    op.create_index('ix_courts_is_active', 'courts', ['is_active'])
    op.create_index('ix_coaches_is_active', 'coaches', ['is_active'])


def downgrade() -> None:
    op.drop_index('ix_courts_establishment_id')
    op.drop_index('ix_bookings_court_date')
    op.drop_index('ix_bookings_coach_date')
    op.drop_index('ix_coach_bookings_coach_date')
    op.drop_index('ix_establishments_is_active')
    op.drop_index('ix_courts_is_active')
    op.drop_index('ix_coaches_is_active')
