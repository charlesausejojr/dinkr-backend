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
    # Enriched venue fields
    court_name: str = ""
    establishment_name: str = ""
    establishment_location: str = ""
    establishment_latitude: float | None = None
    establishment_longitude: float | None = None
    # Enriched coach fields (when include_coach is True)
    coach_name: str = ""
    coach_avatar_url: str | None = None
    coach_bio: str = ""

    model_config = {"from_attributes": True}
