import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.booking import Booking
from app.models.court import Court
from app.models.establishment import Establishment
from app.models.coach import Coach
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingOut
from app.dependencies import get_current_user
from app.services.availability import is_court_available, is_coach_available

router = APIRouter()
logger = logging.getLogger("dinkr")


def calculate_duration_hours(start: str, end: str) -> float:
    sh, sm = map(int, start.split(":"))
    eh, em = map(int, end.split(":"))
    return ((eh * 60 + em) - (sh * 60 + sm)) / 60


@router.post("/", response_model=BookingOut, status_code=201)
async def create_booking(
    payload: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate court exists
    court_res = await db.execute(select(Court).where(Court.id == payload.court_id))
    court = court_res.scalar_one_or_none()
    if not court or not court.is_active:
        raise HTTPException(status_code=404, detail="Court not found")

    # Check court availability
    if not await is_court_available(db, str(payload.court_id), payload.date, payload.start_time, payload.end_time):
        logger.warning("Court %s unavailable on %s %s-%s", payload.court_id, payload.date, payload.start_time, payload.end_time)
        raise HTTPException(status_code=409, detail="Court is not available for the selected time slot")

    # Calculate price
    duration = calculate_duration_hours(payload.start_time, payload.end_time)
    total_price = court.price_per_hour * duration

    # Handle optional coach combo
    coach_id = None
    if payload.include_coach and payload.coach_id:
        coach_res = await db.execute(select(Coach).where(Coach.id == payload.coach_id))
        coach = coach_res.scalar_one_or_none()
        if not coach or not coach.is_active:
            raise HTTPException(status_code=404, detail="Coach not found")

        # CRITICAL: Check coach availability across BOTH booking tables
        if not await is_coach_available(db, str(payload.coach_id), payload.date, payload.start_time, payload.end_time):
            logger.warning("Coach %s unavailable on %s %s-%s", payload.coach_id, payload.date, payload.start_time, payload.end_time)
            raise HTTPException(status_code=409, detail="Coach is not available for the selected time slot")

        coach_id = payload.coach_id
        total_price += coach.rate_per_hour * duration

    booking = Booking(
        court_id=payload.court_id,
        user_id=current_user.id,
        coach_id=coach_id,
        date=payload.date,
        start_time=payload.start_time,
        end_time=payload.end_time,
        total_price=total_price,
        include_coach=payload.include_coach,
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    logger.info(
        "Booking created: id=%s user=%s court=%s date=%s %s-%s total=₱%.2f%s",
        booking.id, current_user.email, court.name, payload.date,
        payload.start_time, payload.end_time, total_price,
        f" + coach={coach_id}" if coach_id else "",
    )
    return booking


@router.get("/my", response_model=list[BookingOut])
async def my_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Booking).where(Booking.user_id == current_user.id).order_by(Booking.date.desc())
    )
    bookings = result.scalars().all()

    # Enrich each booking with court, establishment, and optional coach details
    enriched = []
    for b in bookings:
        court_res = await db.execute(select(Court).where(Court.id == b.court_id))
        court = court_res.scalar_one_or_none()
        est = None
        if court:
            est_res = await db.execute(select(Establishment).where(Establishment.id == court.establishment_id))
            est = est_res.scalar_one_or_none()
        coach = None
        if b.include_coach and b.coach_id:
            coach_res = await db.execute(select(Coach).where(Coach.id == b.coach_id))
            coach = coach_res.scalar_one_or_none()
        enriched.append(BookingOut(
            id=b.id,
            court_id=b.court_id,
            user_id=b.user_id,
            coach_id=b.coach_id,
            date=b.date,
            start_time=b.start_time,
            end_time=b.end_time,
            total_price=b.total_price,
            include_coach=b.include_coach,
            status=b.status,
            created_at=b.created_at,
            court_name=court.name if court else "",
            establishment_name=est.name if est else "",
            establishment_location=est.location if est else "",
            establishment_latitude=est.latitude if est else None,
            establishment_longitude=est.longitude if est else None,
            coach_name=coach.name if coach else "",
            coach_avatar_url=coach.avatar_url if coach else None,
            coach_bio=coach.bio if coach else "",
        ))

    logger.info("Listed %d court bookings for %s", len(bookings), current_user.email)
    return enriched


@router.delete("/{booking_id}", status_code=204)
async def cancel_booking(
    booking_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if str(booking.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    booking.status = "cancelled"
    await db.commit()
    logger.info("Booking cancelled: id=%s by user=%s", booking_id, current_user.email)
