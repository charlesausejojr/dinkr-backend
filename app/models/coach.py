from sqlalchemy import Column, String, Boolean, Float, DateTime, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Coach(Base):
    __tablename__ = "coaches"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    bio = Column(Text)
    rate_per_hour = Column(Float, nullable=False)
    specialties = Column(ARRAY(String), default=[])
    avatar_url = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
