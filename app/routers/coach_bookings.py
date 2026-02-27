import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.coach_booking import CoachBooking
from app.models.coach import Coach
from app.models.user import User
from app.schemas.coach_booking import CoachBookingCreate, CoachBookingOut
from app.dependencies import get_current_user
from app.services.availability import is_coach_available

router = APIRouter()
logger = logging.getLogger("dinkr")


def calculate_duration_hours(start: str, end: str) -> float:
    sh, sm = map(int, start.split(":"))
    eh, em = map(int, end.split(":"))
    return ((eh * 60 + em) - (sh * 60 + sm)) / 60


@router.post("/", response_model=CoachBookingOut, status_code=201)
async def create_coach_booking(
    payload: CoachBookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    coach_res = await db.execute(select(Coach).where(Coach.id == payload.coach_id))
    coach = coach_res.scalar_one_or_none()
    if not coach or not coach.is_active:
        logger.warning("Coach booking failed — coach not found: id=%s", payload.coach_id)
        raise HTTPException(status_code=404, detail="Coach not found")

    if not await is_coach_available(db, str(payload.coach_id), payload.date, payload.start_time, payload.end_time):
        logger.warning(
            "Coach booking conflict: coach='%s' date=%s %s-%s requested by %s",
            coach.name, payload.date, payload.start_time, payload.end_time, current_user.email
        )
        raise HTTPException(status_code=409, detail="Coach is not available for the selected time slot")

    duration = calculate_duration_hours(payload.start_time, payload.end_time)
    total_price = coach.rate_per_hour * duration
    booking = CoachBooking(
        coach_id=payload.coach_id,
        user_id=current_user.id,
        date=payload.date,
        start_time=payload.start_time,
        end_time=payload.end_time,
        total_price=total_price,
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    logger.info(
        "Coach booking created: id=%s coach='%s' date=%s %s-%s total=₱%.2f by %s",
        booking.id, coach.name, payload.date, payload.start_time, payload.end_time,
        total_price, current_user.email
    )
    return booking


@router.get("/my", response_model=list[CoachBookingOut])
async def my_coach_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(CoachBooking).where(CoachBooking.user_id == current_user.id).order_by(CoachBooking.date.desc())
    )
    bookings = result.scalars().all()
    logger.info("Listed %d coach bookings for %s", len(bookings), current_user.email)
    return bookings


@router.delete("/{booking_id}", status_code=204)
async def cancel_coach_booking(
    booking_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(CoachBooking).where(CoachBooking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        logger.warning("Coach booking cancel failed — not found: id=%s", booking_id)
        raise HTTPException(status_code=404, detail="Coach booking not found")
    if str(booking.user_id) != str(current_user.id):
        logger.warning("Coach booking cancel forbidden: id=%s by %s", booking_id, current_user.email)
        raise HTTPException(status_code=403, detail="Not authorized")
    booking.status = "cancelled"
    await db.commit()
    logger.info("Coach booking cancelled: id=%s by %s", booking_id, current_user.email)
