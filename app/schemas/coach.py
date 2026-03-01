from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

DEFAULT_SCHEDULE: dict = {
    day: {"open": "06:00", "close": "22:00", "closed": False}
    for day in DAYS
}


class DaySchedule(BaseModel):
    open: str = "06:00"
    close: str = "22:00"
    closed: bool = False


class CoachCreate(BaseModel):
    name: str
    bio: str | None = None
    rate_per_hour: float
    specialties: list[str] = []
    avatar_url: str | None = None
    schedule: dict[str, DaySchedule] = {d: DaySchedule() for d in DAYS}


class CoachUpdate(BaseModel):
    name: str | None = None
    bio: str | None = None
    rate_per_hour: float | None = None
    specialties: list[str] | None = None
    avatar_url: str | None = None
    schedule: dict[str, DaySchedule] | None = None
    is_active: bool | None = None


class CoachOut(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    bio: str | None
    rate_per_hour: float
    specialties: list[str]
    avatar_url: str | None
    schedule: dict
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
