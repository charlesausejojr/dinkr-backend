from sqlalchemy import Column, String, Boolean, Float, DateTime, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.database import Base
import uuid

DEFAULT_SCHEDULE = {
    day: {"open": "06:00", "close": "22:00", "closed": False}
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
}


class Coach(Base):
    __tablename__ = "coaches"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    bio = Column(Text)
    rate_per_hour = Column(Float, nullable=False)
    specialties = Column(ARRAY(String), default=[])
    avatar_url = Column(String)
    schedule = Column(JSONB, nullable=False, default=DEFAULT_SCHEDULE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
