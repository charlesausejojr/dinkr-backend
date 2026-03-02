from sqlalchemy import Column, String, Boolean, DateTime, Text, ARRAY, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

DEFAULT_SCHEDULE = {
    day: {"open": "06:00", "close": "22:00", "closed": False}
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
}


class Establishment(Base):
    __tablename__ = "establishments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    description = Column(Text)
    amenities = Column(ARRAY(String), default=[])
    images = Column(ARRAY(String), default=[])
    schedule = Column(JSONB, nullable=False, default=DEFAULT_SCHEDULE)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    courts = relationship("Court", back_populates="establishment", lazy="selectin")
