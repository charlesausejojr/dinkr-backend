from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime


class CoachBookingCreate(BaseModel):
    coach_id: UUID
    date: date
    start_time: str
    end_time: str


class CoachBookingOut(BaseModel):
    id: UUID
    coach_id: UUID
    user_id: UUID
    date: date
    start_time: str
    end_time: str
    total_price: float
    status: str
    created_at: datetime
    # Enriched coach fields
    coach_name: str = ""
    coach_avatar_url: str | None = None
    coach_bio: str = ""

    model_config = {"from_attributes": True}
