import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.establishment import Establishment
from app.models.court import Court
from app.models.user import User
from app.schemas.establishment import EstablishmentCreate, EstablishmentUpdate, EstablishmentOut, EstablishmentWithCourts
from app.schemas.court import CourtCreate, CourtUpdate, CourtOut
from app.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger("dinkr")


# ── Establishment CRUD ──────────────────────────────────────────────────────

@router.get("/", response_model=list[EstablishmentOut])
async def list_establishments(
    skip: int = 0,
    limit: int = 20,
    location: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Establishment).where(Establishment.is_active == True)
    if location:
        query = query.where(Establishment.location.ilike(f"%{location}%"))
    result = await db.execute(query.offset(skip).limit(limit))
    ests = result.scalars().all()
    logger.info("Listed %d establishments (location=%s)", len(ests), location or "*")
    return ests


@router.get("/{establishment_id}", response_model=EstablishmentWithCourts)
async def get_establishment(establishment_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Establishment).where(Establishment.id == establishment_id))
    est = result.scalar_one_or_none()
    if not est:
        logger.warning("Establishment not found: id=%s", establishment_id)
        raise HTTPException(status_code=404, detail="Establishment not found")
    logger.info("Fetched establishment: '%s' (id=%s)", est.name, establishment_id)
    return est


@router.post("/", response_model=EstablishmentOut, status_code=201)
async def create_establishment(
    payload: EstablishmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    est = Establishment(**payload.model_dump(), owner_id=current_user.id)
    db.add(est)
    await db.commit()
    await db.refresh(est)
    logger.info("Establishment created: '%s' (id=%s) by %s", est.name, est.id, current_user.email)
    return est


@router.patch("/{establishment_id}", response_model=EstablishmentOut)
async def update_establishment(
    establishment_id: str,
    payload: EstablishmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Establishment).where(Establishment.id == establishment_id))
    est = result.scalar_one_or_none()
    if not est:
        raise HTTPException(status_code=404, detail="Establishment not found")
    if str(est.owner_id) != str(current_user.id):
        logger.warning("Establishment update forbidden: id=%s requested by %s", establishment_id, current_user.email)
        raise HTTPException(status_code=403, detail="Not authorized")
    updated_fields = list(payload.model_dump(exclude_unset=True).keys())
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(est, field, value)
    await db.commit()
    await db.refresh(est)
    logger.info("Establishment updated: '%s' (id=%s) fields=%s by %s", est.name, establishment_id, updated_fields, current_user.email)
    return est


@router.delete("/{establishment_id}", status_code=204)
async def delete_establishment(
    establishment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Establishment).where(Establishment.id == establishment_id))
    est = result.scalar_one_or_none()
    if not est:
        logger.warning("Establishment delete failed — not found: id=%s", establishment_id)
        raise HTTPException(status_code=404, detail="Establishment not found")
    if str(est.owner_id) != str(current_user.id):
        logger.warning("Establishment delete forbidden: id=%s requested by %s", establishment_id, current_user.email)
        raise HTTPException(status_code=403, detail="Not authorized")
    est.is_active = False
    await db.commit()
    logger.info("Establishment deactivated: '%s' (id=%s) by %s", est.name, establishment_id, current_user.email)


# ── Courts nested under Establishment ──────────────────────────────────────

@router.get("/{establishment_id}/courts", response_model=list[CourtOut])
async def list_courts(establishment_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Court).where(
            Court.establishment_id == establishment_id,
            Court.is_active == True
        )
    )
    courts = result.scalars().all()
    logger.info("Listed %d courts for est=%s", len(courts), establishment_id)
    return courts


@router.post("/{establishment_id}/courts", response_model=CourtOut, status_code=201)
async def add_court(
    establishment_id: str,
    payload: CourtCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    est_result = await db.execute(select(Establishment).where(Establishment.id == establishment_id))
    est = est_result.scalar_one_or_none()
    if not est:
        logger.warning("Add court failed — establishment not found: id=%s", establishment_id)
        raise HTTPException(status_code=404, detail="Establishment not found")
    if str(est.owner_id) != str(current_user.id):
        logger.warning("Add court forbidden: est=%s requested by %s", establishment_id, current_user.email)
        raise HTTPException(status_code=403, detail="Not authorized")
    court = Court(**payload.model_dump(), establishment_id=establishment_id)
    db.add(court)
    await db.commit()
    await db.refresh(court)
    logger.info("Court added: '%s' to est=%s by %s", court.name, establishment_id, current_user.email)
    return court


@router.patch("/{establishment_id}/courts/{court_id}", response_model=CourtOut)
async def update_court(
    establishment_id: str,
    court_id: str,
    payload: CourtUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    est_result = await db.execute(select(Establishment).where(Establishment.id == establishment_id))
    est = est_result.scalar_one_or_none()
    if not est or str(est.owner_id) != str(current_user.id):
        logger.warning("Court update forbidden: court=%s est=%s requested by %s", court_id, establishment_id, current_user.email)
        raise HTTPException(status_code=403, detail="Not authorized")
    court_result = await db.execute(
        select(Court).where(Court.id == court_id, Court.establishment_id == establishment_id)
    )
    court = court_result.scalar_one_or_none()
    if not court:
        logger.warning("Court update failed — not found: id=%s in est=%s", court_id, establishment_id)
        raise HTTPException(status_code=404, detail="Court not found")
    updated_fields = list(payload.model_dump(exclude_unset=True).keys())
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(court, field, value)
    await db.commit()
    await db.refresh(court)
    logger.info("Court updated: '%s' (id=%s) fields=%s in est=%s by %s", court.name, court_id, updated_fields, establishment_id, current_user.email)
    return court


@router.delete("/{establishment_id}/courts/{court_id}", status_code=204)
async def remove_court(
    establishment_id: str,
    court_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    est_result = await db.execute(select(Establishment).where(Establishment.id == establishment_id))
    est = est_result.scalar_one_or_none()
    if not est or str(est.owner_id) != str(current_user.id):
        logger.warning("Court deactivate forbidden: court=%s est=%s requested by %s", court_id, establishment_id, current_user.email)
        raise HTTPException(status_code=403, detail="Not authorized")
    court_result = await db.execute(
        select(Court).where(Court.id == court_id, Court.establishment_id == establishment_id)
    )
    court = court_result.scalar_one_or_none()
    if not court:
        logger.warning("Court deactivate failed — not found: id=%s in est=%s", court_id, establishment_id)
        raise HTTPException(status_code=404, detail="Court not found")
    court.is_active = False
    await db.commit()
    logger.info("Court deactivated: '%s' (id=%s) in est=%s by %s", court.name, court_id, establishment_id, current_user.email)
