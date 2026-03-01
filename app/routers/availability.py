import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
from app.database import get_db
from app.models.court import Court
from app.models.establishment import Establishment
from app.models.coach import Coach
from app.services.availability import get_court_available_slots, get_coach_available_slots

router = APIRouter()
logger = logging.getLogger("dinkr")

_DEFAULT_OPEN  = "06:00"
_DEFAULT_CLOSE = "22:00"
_WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def generate_slots(open_time: str, close_time: str) -> list[str]:
    """Return hourly boundary strings from open_time to close_time inclusive."""
    oh, om = map(int, open_time.split(":"))
    ch, cm = map(int, close_time.split(":"))
    slots, t = [], oh * 60 + om
    while t <= ch * 60 + cm:
        slots.append(f"{t // 60:02d}:{t % 60:02d}")
        t += 60
    return slots


@router.get("/court/{court_id}")
async def court_availability(
    court_id: str,
    date: date = Query(...),
    db: AsyncSession = Depends(get_db)
):
    court_row = await db.execute(select(Court).where(Court.id == court_id))
    court = court_row.scalar_one_or_none()
    if not court:
        raise HTTPException(status_code=404, detail="Court not found")

    est_row = await db.execute(select(Establishment).where(Establishment.id == court.establishment_id))
    est = est_row.scalar_one_or_none()

    # Look up today's day-of-week in the establishment's schedule
    day_name = _WEEKDAYS[date.weekday()]
    day = (est.schedule or {}).get(day_name, {}) if est else {}

    if day.get("closed", False):
        logger.info("Court availability: id=%s date=%s (%s) → CLOSED", court_id, date, day_name)
        return {"court_id": court_id, "date": str(date), "slots": [], "closed": True}

    open_time  = day.get("open",  _DEFAULT_OPEN)
    close_time = day.get("close", _DEFAULT_CLOSE)
    time_slots = generate_slots(open_time, close_time)

    slots = await get_court_available_slots(db, court_id, date, time_slots)
    available = sum(1 for s in slots if s["is_available"])
    logger.info(
        "Court availability: id=%s date=%s (%s) %s–%s → %d/%d free",
        court_id, date, day_name, open_time, close_time, available, len(slots)
    )
    return {"court_id": court_id, "date": str(date), "slots": slots, "closed": False}


@router.get("/coach/{coach_id}")
async def coach_availability(
    coach_id: str,
    date: date = Query(...),
    db: AsyncSession = Depends(get_db)
):
    coach_row = await db.execute(select(Coach).where(Coach.id == coach_id))
    coach = coach_row.scalar_one_or_none()

    day_name = _WEEKDAYS[date.weekday()]
    day = (coach.schedule or {}).get(day_name, {}) if coach else {}

    if day.get("closed", False):
        logger.info("Coach availability: id=%s date=%s (%s) → UNAVAILABLE", coach_id, date, day_name)
        return {"coach_id": coach_id, "date": str(date), "slots": [], "closed": True}

    open_time  = day.get("open",  _DEFAULT_OPEN)
    close_time = day.get("close", _DEFAULT_CLOSE)
    time_slots = generate_slots(open_time, close_time)

    slots = await get_coach_available_slots(db, coach_id, date, time_slots)
    available = sum(1 for s in slots if s["is_available"])
    logger.info("Coach availability: id=%s date=%s (%s) %s–%s → %d/%d free", coach_id, date, day_name, open_time, close_time, available, len(slots))
    return {"coach_id": coach_id, "date": str(date), "slots": slots, "closed": False}
