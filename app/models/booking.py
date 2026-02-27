from sqlalchemy import Column, String, Boolean, Float, DateTime, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Booking(Base):
    """Court booking — optionally includes a coach (combo booking)."""
    __tablename__ = "bookings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    court_id = Column(UUID(as_uuid=True), ForeignKey("courts.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    coach_id = Column(UUID(as_uuid=True), ForeignKey("coaches.id"), nullable=True)
    date = Column(Date, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    total_price = Column(Float, nullable=False)
    include_coach = Column(Boolean, default=False)
    status = Column(String, default="confirmed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
