import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.database import get_db
from app.services.availability import get_court_available_slots, get_coach_available_slots

router = APIRouter()
logger = logging.getLogger("dinkr")

TIME_SLOTS = [
    "06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00",
    "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00"
]


@router.get("/court/{court_id}")
async def court_availability(
    court_id: str,
    date: date = Query(...),
    db: AsyncSession = Depends(get_db)
):
    slots = await get_court_available_slots(db, court_id, date, TIME_SLOTS)
    available = sum(1 for s in slots if s["is_available"])
    logger.info("Court availability: id=%s date=%s → %d/%d slots free", court_id, date, available, len(slots))
    return {"court_id": court_id, "date": str(date), "slots": slots}


@router.get("/coach/{coach_id}")
async def coach_availability(
    coach_id: str,
    date: date = Query(...),
    db: AsyncSession = Depends(get_db)
):
    slots = await get_coach_available_slots(db, coach_id, date, TIME_SLOTS)
    available = sum(1 for s in slots if s["is_available"])
    logger.info("Coach availability: id=%s date=%s → %d/%d slots free", coach_id, date, available, len(slots))
    return {"coach_id": coach_id, "date": str(date), "slots": slots}
