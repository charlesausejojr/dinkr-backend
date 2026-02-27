import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.coach import Coach
from app.models.user import User
from app.schemas.coach import CoachCreate, CoachUpdate, CoachOut
from app.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger("dinkr")


@router.get("/", response_model=list[CoachOut])
async def list_coaches(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Coach).where(Coach.is_active == True).offset(skip).limit(limit)
    )
    coaches = result.scalars().all()
    logger.info("Listed %d coaches (skip=%d limit=%d)", len(coaches), skip, limit)
    return coaches


@router.get("/{coach_id}", response_model=CoachOut)
async def get_coach(coach_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Coach).where(Coach.id == coach_id))
    coach = result.scalar_one_or_none()
    if not coach:
        logger.warning("Coach not found: id=%s", coach_id)
        raise HTTPException(status_code=404, detail="Coach not found")
    logger.info("Fetched coach: '%s' (id=%s)", coach.name, coach_id)
    return coach


@router.post("/", response_model=CoachOut, status_code=201)
async def create_coach(
    payload: CoachCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    coach = Coach(**payload.model_dump(), user_id=current_user.id)
    db.add(coach)
    await db.commit()
    await db.refresh(coach)
    logger.info("Coach listing created: '%s' (id=%s) by %s", coach.name, coach.id, current_user.email)
    return coach


@router.patch("/{coach_id}", response_model=CoachOut)
async def update_coach(
    coach_id: str,
    payload: CoachUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Coach).where(Coach.id == coach_id))
    coach = result.scalar_one_or_none()
    if not coach:
        logger.warning("Coach update failed — not found: id=%s", coach_id)
        raise HTTPException(status_code=404, detail="Coach not found")
    if str(coach.user_id) != str(current_user.id):
        logger.warning("Coach update forbidden: id=%s requested by %s", coach_id, current_user.email)
        raise HTTPException(status_code=403, detail="Not authorized")
    updated_fields = list(payload.model_dump(exclude_unset=True).keys())
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(coach, field, value)
    await db.commit()
    await db.refresh(coach)
    logger.info("Coach updated: '%s' (id=%s) fields=%s by %s", coach.name, coach_id, updated_fields, current_user.email)
    return coach


@router.delete("/{coach_id}", status_code=204)
async def delete_coach(
    coach_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Coach).where(Coach.id == coach_id))
    coach = result.scalar_one_or_none()
    if not coach:
        logger.warning("Coach deactivate failed — not found: id=%s", coach_id)
        raise HTTPException(status_code=404, detail="Coach not found")
    if str(coach.user_id) != str(current_user.id):
        logger.warning("Coach deactivate forbidden: id=%s requested by %s", coach_id, current_user.email)
        raise HTTPException(status_code=403, detail="Not authorized")
    coach.is_active = False
    await db.commit()
    logger.info("Coach deactivated: '%s' (id=%s) by %s", coach.name, coach_id, current_user.email)
