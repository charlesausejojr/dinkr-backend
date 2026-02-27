from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.schemas.court import CourtOut


class EstablishmentCreate(BaseModel):
    name: str
    location: str
    description: str | None = None
    amenities: list[str] = []
    images: list[str] = []


class EstablishmentUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    description: str | None = None
    amenities: list[str] | None = None
    images: list[str] | None = None
    is_active: bool | None = None


class EstablishmentOut(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    location: str
    description: str | None
    amenities: list[str]
    images: list[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class EstablishmentWithCourts(EstablishmentOut):
    """Used when fetching a single establishment — includes its courts."""
    courts: list[CourtOut] = []
