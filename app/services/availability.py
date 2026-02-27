from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.booking import Booking
from app.models.coach_booking import CoachBooking
from datetime import date


def times_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
    """Check if two time ranges overlap. Times are 'HH:MM' strings."""
    return start1 < end2 and start2 < end1


async def is_court_available(
    db: AsyncSession,
    court_id: str,
    booking_date: date,
    start_time: str,
    end_time: str,
    exclude_booking_id: str | None = None
) -> bool:
    """Returns True if the court has no confirmed booking overlapping the given slot."""
    query = select(Booking).where(
        and_(
            Booking.court_id == court_id,
            Booking.date == booking_date,
            Booking.status == "confirmed",
        )
    )
    if exclude_booking_id:
        query = query.where(Booking.id != exclude_booking_id)

    result = await db.execute(query)
    existing = result.scalars().all()

    for b in existing:
        if times_overlap(start_time, end_time, b.start_time, b.end_time):
            return False
    return True


async def is_coach_available(
    db: AsyncSession,
    coach_id: str,
    booking_date: date,
    start_time: str,
    end_time: str,
    exclude_booking_id: str | None = None,
    exclude_coach_booking_id: str | None = None
) -> bool:
    """
    Returns True if the coach is free in the given slot.
    Checks BOTH the bookings table (combo bookings) AND the coach_bookings table (standalone).
    This is the critical dual-check for coach availability.
    """
    # Check combo bookings (court bookings that include this coach)
    q1 = select(Booking).where(
        and_(
            Booking.coach_id == coach_id,
            Booking.date == booking_date,
            Booking.status == "confirmed",
            Booking.include_coach == True,
        )
    )
    if exclude_booking_id:
        q1 = q1.where(Booking.id != exclude_booking_id)

    res1 = await db.execute(q1)
    for b in res1.scalars().all():
        if times_overlap(start_time, end_time, b.start_time, b.end_time):
            return False

    # Check standalone coach bookings
    q2 = select(CoachBooking).where(
        and_(
            CoachBooking.coach_id == coach_id,
            CoachBooking.date == booking_date,
            CoachBooking.status == "confirmed",
        )
    )
    if exclude_coach_booking_id:
        q2 = q2.where(CoachBooking.id != exclude_coach_booking_id)

    res2 = await db.execute(q2)
    for cb in res2.scalars().all():
        if times_overlap(start_time, end_time, cb.start_time, cb.end_time):
            return False

    return True


async def get_court_available_slots(
    db: AsyncSession,
    court_id: str,
    booking_date: date,
    time_slots: list[str]
) -> list[dict]:
    """Return list of slots with availability status for a court."""
    slots = []
    for i in range(len(time_slots) - 1):
        start = time_slots[i]
        end = time_slots[i + 1]
        available = await is_court_available(db, court_id, booking_date, start, end)
        slots.append({"start_time": start, "end_time": end, "is_available": available})
    return slots


async def get_coach_available_slots(
    db: AsyncSession,
    coach_id: str,
    booking_date: date,
    time_slots: list[str]
) -> list[dict]:
    """Return list of slots with availability status for a coach."""
    slots = []
    for i in range(len(time_slots) - 1):
        start = time_slots[i]
        end = time_slots[i + 1]
        available = await is_coach_available(db, coach_id, booking_date, start, end)
        slots.append({"start_time": start, "end_time": end, "is_available": available})
    return slots
