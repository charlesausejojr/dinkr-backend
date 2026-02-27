import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.court import Court
from app.schemas.court import CourtOut

router = APIRouter()
logger = logging.getLogger("dinkr")


@router.get("/{court_id}", response_model=CourtOut)
async def get_court(court_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Court).where(Court.id == court_id))
    court = result.scalar_one_or_none()
    if not court:
        logger.warning("Court not found: id=%s", court_id)
        raise HTTPException(status_code=404, detail="Court not found")
    logger.info("Fetched court: '%s' (id=%s)", court.name, court_id)
    return court
