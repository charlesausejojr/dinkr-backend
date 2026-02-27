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

    model_config = {"from_attributes": True}
