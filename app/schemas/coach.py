from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class CoachCreate(BaseModel):
    name: str
    bio: str | None = None
    rate_per_hour: float
    specialties: list[str] = []
    avatar_url: str | None = None


class CoachUpdate(BaseModel):
    name: str | None = None
    bio: str | None = None
    rate_per_hour: float | None = None
    specialties: list[str] | None = None
    avatar_url: str | None = None
    is_active: bool | None = None


class CoachOut(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    bio: str | None
    rate_per_hour: float
    specialties: list[str]
    avatar_url: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
