from sqlalchemy import Column, String, Boolean, DateTime, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class Establishment(Base):
    __tablename__ = "establishments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    description = Column(Text)
    amenities = Column(ARRAY(String), default=[])
    images = Column(ARRAY(String), default=[])
    open_time = Column(String, nullable=False, server_default="06:00")
    close_time = Column(String, nullable=False, server_default="22:00")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    courts = relationship("Court", back_populates="establishment", lazy="selectin")
