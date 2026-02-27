from pydantic import BaseModel, model_validator
from uuid import UUID
from datetime import date, datetime


class BookingCreate(BaseModel):
    court_id: UUID
    date: date
    start_time: str
    end_time: str
    include_coach: bool = False
    coach_id: UUID | None = None

    @model_validator(mode="after")
    def check_coach_required(self):
        if self.include_coach and not self.coach_id:
            raise ValueError("coach_id is required when include_coach is True")
        return self


class BookingOut(BaseModel):
    id: UUID
    court_id: UUID
    user_id: UUID
    coach_id: UUID | None
    date: date
    start_time: str
    end_time: str
    total_price: float
    include_coach: bool
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
