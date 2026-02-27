import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
from app.database import get_db
from app.models.court import Court
from app.models.establishment import Establishment
from app.services.availability import get_court_available_slots, get_coach_available_slots

router = APIRouter()
logger = logging.getLogger("dinkr")

# Default range used for coach availability (not tied to any establishment)
_DEFAULT_OPEN = "06:00"
_DEFAULT_CLOSE = "22:00"


def generate_slots(open_time: str, close_time: str) -> list[str]:
    """Return hourly boundary strings from open_time to close_time inclusive."""
    oh, om = map(int, open_time.split(":"))
    ch, cm = map(int, close_time.split(":"))
    open_min = oh * 60 + om
    close_min = ch * 60 + cm
    slots = []
    t = open_min
    while t <= close_min:
        slots.append(f"{t // 60:02d}:{t % 60:02d}")
        t += 60
    return slots


@router.get("/court/{court_id}")
async def court_availability(
    court_id: str,
    date: date = Query(...),
    db: AsyncSession = Depends(get_db)
):
    # Load the court and its establishment to get operating hours
    court_row = await db.execute(select(Court).where(Court.id == court_id))
    court = court_row.scalar_one_or_none()
    if not court:
        raise HTTPException(status_code=404, detail="Court not found")

    est_row = await db.execute(select(Establishment).where(Establishment.id == court.establishment_id))
    est = est_row.scalar_one_or_none()

    open_time = est.open_time if est else _DEFAULT_OPEN
    close_time = est.close_time if est else _DEFAULT_CLOSE
    time_slots = generate_slots(open_time, close_time)

    slots = await get_court_available_slots(db, court_id, date, time_slots)
    available = sum(1 for s in slots if s["is_available"])
    logger.info(
        "Court availability: id=%s date=%s hours=%s–%s → %d/%d slots free",
        court_id, date, open_time, close_time, available, len(slots)
    )
    return {"court_id": court_id, "date": str(date), "slots": slots}


@router.get("/coach/{coach_id}")
async def coach_availability(
    coach_id: str,
    date: date = Query(...),
    db: AsyncSession = Depends(get_db)
):
    time_slots = generate_slots(_DEFAULT_OPEN, _DEFAULT_CLOSE)
    slots = await get_coach_available_slots(db, coach_id, date, time_slots)
    available = sum(1 for s in slots if s["is_available"])
    logger.info("Coach availability: id=%s date=%s → %d/%d slots free", coach_id, date, available, len(slots))
    return {"coach_id": coach_id, "date": str(date), "slots": slots}
