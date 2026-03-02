from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.schemas.court import CourtOut

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

DEFAULT_SCHEDULE: dict = {
    day: {"open": "06:00", "close": "22:00", "closed": False}
    for day in DAYS
}


class DaySchedule(BaseModel):
    open: str = "06:00"
    close: str = "22:00"
    closed: bool = False


class EstablishmentCreate(BaseModel):
    name: str
    location: str
    description: str | None = None
    amenities: list[str] = []
    images: list[str] = []
    schedule: dict[str, DaySchedule] = {d: DaySchedule() for d in DAYS}
    latitude: float | None = None
    longitude: float | None = None


class EstablishmentUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    description: str | None = None
    amenities: list[str] | None = None
    images: list[str] | None = None
    schedule: dict[str, DaySchedule] | None = None
    latitude: float | None = None
    longitude: float | None = None
    is_active: bool | None = None


class EstablishmentOut(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    location: str
    description: str | None
    amenities: list[str]
    images: list[str]
    schedule: dict
    latitude: float | None
    longitude: float | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class EstablishmentWithCourts(EstablishmentOut):
    """Used when fetching a single establishment — includes its courts."""
    courts: list[CourtOut] = []
