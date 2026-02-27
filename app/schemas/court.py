from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class CourtCreate(BaseModel):
    name: str
    description: str | None = None
    price_per_hour: float
    surface_type: str | None = None


class CourtUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price_per_hour: float | None = None
    surface_type: str | None = None
    is_active: bool | None = None


class CourtOut(BaseModel):
    id: UUID
    establishment_id: UUID
    name: str
    description: str | None
    price_per_hour: float
    surface_type: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
